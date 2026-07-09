import json
from datetime import date

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..decorators import requer_chave_interna
from ..middleware import set_current_user


def _serializar_auditoria(auditoria):
    return {
        'id_unico': str(auditoria.id_unico),
        'nome_auditoria': auditoria.nome_auditoria,
        'orgao': auditoria.orgao,
        'status': auditoria.status,
    }


# Campos do EtapaForm espelhados pelo app mobile — usados tanto pra listar
# (pré-popular edição) quanto pra montar o `baseline` de detecção de
# conflito (ver api_mobile_editar_etapa). Se um campo aqui não bater com o
# que o app mandou como baseline, é sinal de que alguém mudou a Etapa nesse
# meio-tempo.
_CAMPOS_ETAPA = ['orientacao', 'documentos', 'atividade', 'prazo', 'situacao', 'metodo']


def _serializar_etapa(etapa):
    return {
        'id_unico': str(etapa.id_unico),
        'orientacao': etapa.orientacao,
        'documentos': etapa.documentos,
        'atividade': etapa.atividade,
        'prazo': etapa.prazo.isoformat() if etapa.prazo else None,
        'situacao': etapa.situacao,
        'metodo': etapa.metodo,
    }


def _campos_etapa_para_comparacao(etapa):
    """Mesmo formato de _serializar_etapa, mas sem id_unico — usado para
    comparar contra o `baseline`/`dados_atuais` enviados/guardados como JSON."""
    dados = _serializar_etapa(etapa)
    dados.pop('id_unico')
    return dados


def _buscar_usuario(usuario_uuid):
    """
    Lookup explícito (em vez de get_object_or_404) porque esta é uma API
    JSON consumida pelo sync-backend, não uma view de browser — a página de
    erro HTML padrão do Django não serve para um cliente que espera JSON.
    """
    from ..models import Usuario
    try:
        return Usuario.objects.get(id_unico=usuario_uuid), None
    except (Usuario.DoesNotExist, ValueError, ValidationError):
        return None, JsonResponse({'detail': 'Usuário não encontrado.'}, status=404)


@csrf_exempt
@requer_chave_interna
@require_GET
def api_mobile_auditorias(request):
    """
    Lista leve (sem etapas) das Auditorias em que o usuário está envolvido —
    alimenta a tela de seleção do app de campo. As etapas só são buscadas
    depois que o auditor escolhe uma auditoria específica (ver
    api_mobile_etapas), para não inchar o banco offline do celular.
    """
    from ..models import Auditoria

    usuario_uuid = request.GET.get('usuario_uuid')
    if not usuario_uuid:
        return JsonResponse({'detail': 'usuario_uuid é obrigatório.'}, status=400)

    usuario, erro = _buscar_usuario(usuario_uuid)
    if erro:
        return erro

    qs = Auditoria.objects.filter(
        usuarios_envolvidos=usuario,
        status__in=['PLANEJADA', 'EM_ANDAMENTO'],
    ).order_by('-data_criacao')

    return JsonResponse({'results': [_serializar_auditoria(a) for a in qs]})


@csrf_exempt
@requer_chave_interna
@require_GET
def api_mobile_etapas(request, id_unico):
    """
    Etapas de UMA auditoria específica — chamado só depois que o auditor
    seleciona a auditoria na tela de seleção (pull sob demanda, não junto
    com a lista de auditorias).
    """
    from ..models import Auditoria

    usuario_uuid = request.GET.get('usuario_uuid')
    if not usuario_uuid:
        return JsonResponse({'detail': 'usuario_uuid é obrigatório.'}, status=400)

    usuario, erro = _buscar_usuario(usuario_uuid)
    if erro:
        return erro

    try:
        auditoria = Auditoria.objects.get(id_unico=id_unico)
    except (Auditoria.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({'detail': 'Auditoria não encontrada.'}, status=404)

    if not auditoria.usuarios_envolvidos.filter(pk=usuario.pk).exists():
        return JsonResponse({'detail': 'Usuário não está envolvido nesta auditoria.'}, status=403)

    etapas = auditoria.etapas_list.all()
    return JsonResponse({'results': [_serializar_etapa(e) for e in etapas]})


@csrf_exempt
@requer_chave_interna
@require_POST
def api_mobile_criar_achado(request):
    """
    Cria um Achado através do ORM do Django (nunca via escrita direta no
    Postgres do sync-backend) — é o único jeito de manter o signal de
    Audit by Design (HistoricoAlteracoes) disparando corretamente, com o
    usuário correto atribuído via impersonação (set_current_user).

    Idempotente por origem_mobile_uuid: um retry de rede do app após um
    sucesso não cria um segundo Achado.
    """
    from ..models import Etapa, Achado

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Corpo da requisição inválido.'}, status=400)

    usuario_uuid = body.get('usuario_uuid')
    etapa_uuid = body.get('etapa_uuid')
    descricao = body.get('descricao')
    origem_mobile_uuid = body.get('origem_mobile_uuid')

    if not all([usuario_uuid, etapa_uuid, descricao, origem_mobile_uuid]):
        return JsonResponse(
            {'detail': 'usuario_uuid, etapa_uuid, descricao e origem_mobile_uuid são obrigatórios.'},
            status=400,
        )

    usuario, erro = _buscar_usuario(usuario_uuid)
    if erro:
        return erro

    try:
        etapa = Etapa.objects.select_related('auditoria').get(id_unico=etapa_uuid)
    except (Etapa.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({'detail': 'Etapa não encontrada.'}, status=404)

    if not usuario.tem_permissao('auditorias', 'editar'):
        return JsonResponse({'detail': 'Perfil sem permissão para registrar achados.'}, status=403)
    if not etapa.auditoria.usuarios_envolvidos.filter(pk=usuario.pk).exists():
        return JsonResponse({'detail': 'Usuário não está envolvido na auditoria desta etapa.'}, status=403)

    try:
        with set_current_user(usuario):
            achado, _criado = Achado.objects.get_or_create(
                origem_mobile_uuid=origem_mobile_uuid,
                defaults={'etapa': etapa, 'usuario': usuario, 'descricao': descricao},
            )
    except (ValueError, ValidationError):
        return JsonResponse({'detail': 'origem_mobile_uuid inválido.'}, status=400)

    return JsonResponse({
        'id_unico': str(achado.id_unico),
        'data_achado': achado.data_achado.isoformat(),
    })


def determinar_resolvedor(auditoria, usuario_originador, usuario_atual):
    """
    Decide quem resolve um conflito de edição concorrente: entre o usuário
    que tentou a edição bloqueada (`usuario_originador`) e o usuário da
    última alteração já persistida (`usuario_atual`), quem tiver
    profundidade MENOR na árvore de Perfil (mais perto da raiz = nível de
    acesso maior) decide. Empate escala para um administrador de
    profundidade estritamente menor, não envolvido em nenhuma das duas
    edições — preferindo alguém já envolvido na auditoria (mais contexto).
    Se ninguém for elegível, devolve None — o conflito fica sem atribuição
    automática, pendente de intervenção manual de um superusuário.
    """
    from ..models import Usuario

    if usuario_atual is None or usuario_atual.pk == usuario_originador.pk:
        return usuario_originador

    prof_originador = usuario_originador.perfil.profundidade() if usuario_originador.perfil else None
    prof_atual = usuario_atual.perfil.profundidade() if usuario_atual.perfil else None

    if prof_originador is None and prof_atual is None:
        return None
    if prof_originador is None:
        return usuario_atual
    if prof_atual is None:
        return usuario_originador
    if prof_originador < prof_atual:
        return usuario_originador
    if prof_atual < prof_originador:
        return usuario_atual

    envolvidos_ids = {usuario_originador.pk, usuario_atual.pk}
    candidatos = Usuario.objects.filter(perfil__isnull=False).exclude(pk__in=envolvidos_ids)

    def mais_senior(queryset):
        elegiveis = [u for u in queryset if u.perfil.profundidade() < prof_originador]
        return min(elegiveis, key=lambda u: u.perfil.profundidade()) if elegiveis else None

    envolvidos_na_auditoria = candidatos.filter(id_unico__in=auditoria.usuarios_envolvidos.values('id_unico'))
    return mais_senior(envolvidos_na_auditoria) or mais_senior(candidatos)


@csrf_exempt
@requer_chave_interna
@require_POST
def api_mobile_criar_etapa(request):
    """
    Cria uma Etapa através do ORM (mesmo motivo de api_mobile_criar_achado:
    é o único jeito do signal de Audit by Design disparar corretamente).
    Idempotente por origem_mobile_uuid. `usuario` (responsável) é sempre o
    próprio auditor autenticado — o app mobile não oferece seletor de
    responsável (decisão de escopo, ver plano de integração fase 2).
    """
    from ..models import Auditoria, Etapa

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Corpo da requisição inválido.'}, status=400)

    usuario_uuid = body.get('usuario_uuid')
    auditoria_uuid = body.get('auditoria_uuid')
    origem_mobile_uuid = body.get('origem_mobile_uuid')
    orientacao = body.get('orientacao')
    atividade = body.get('atividade')
    prazo_str = body.get('prazo')

    if not all([usuario_uuid, auditoria_uuid, origem_mobile_uuid, orientacao, atividade, prazo_str]):
        return JsonResponse(
            {'detail': 'usuario_uuid, auditoria_uuid, origem_mobile_uuid, orientacao, atividade e prazo são obrigatórios.'},
            status=400,
        )

    try:
        prazo = date.fromisoformat(prazo_str)
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'prazo inválido (esperado AAAA-MM-DD).'}, status=400)

    usuario, erro = _buscar_usuario(usuario_uuid)
    if erro:
        return erro

    try:
        auditoria = Auditoria.objects.get(id_unico=auditoria_uuid)
    except (Auditoria.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({'detail': 'Auditoria não encontrada.'}, status=404)

    if not usuario.tem_permissao('auditorias', 'editar'):
        return JsonResponse({'detail': 'Perfil sem permissão para criar etapas.'}, status=403)
    if not auditoria.usuarios_envolvidos.filter(pk=usuario.pk).exists():
        return JsonResponse({'detail': 'Usuário não está envolvido nesta auditoria.'}, status=403)

    try:
        with set_current_user(usuario):
            etapa, _criada = Etapa.objects.get_or_create(
                origem_mobile_uuid=origem_mobile_uuid,
                defaults={
                    'auditoria': auditoria,
                    'usuario': usuario,
                    'orientacao': orientacao,
                    'documentos': body.get('documentos') or '',
                    'atividade': atividade,
                    'prazo': prazo,
                    'situacao': body.get('situacao') or 'PENDENTE',
                    'metodo': body.get('metodo') or '',
                },
            )
    except (ValueError, ValidationError):
        return JsonResponse({'detail': 'origem_mobile_uuid inválido.'}, status=400)

    return JsonResponse(_serializar_etapa(etapa))


@csrf_exempt
@requer_chave_interna
@require_POST
def api_mobile_editar_etapa(request, id_unico):
    """
    Substitui todos os campos da Etapa (replace completo, não patch parcial)
    — combina com a idempotência de "reaplicar os mesmos valores num retry
    é seguro". Antes de aplicar, compara o `baseline` que o app mandou
    (o que ele achava ser o estado atual quando começou a editar) contra o
    estado real persistido agora: se bater, aplica normalmente; se algo
    divergir — não importa se a mudança veio de outro dispositivo, de uma
    edição direta no site, ou de qualquer outra origem — não aplica nada e
    registra um ConflitoEtapa para decisão humana (ver determinar_resolvedor).
    """
    from ..models import Etapa, ConflitoEtapa, HistoricoAlteracoes

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Corpo da requisição inválido.'}, status=400)

    usuario_uuid = body.get('usuario_uuid')
    baseline = body.get('baseline')
    if not usuario_uuid or not isinstance(baseline, dict):
        return JsonResponse({'detail': 'usuario_uuid e baseline são obrigatórios.'}, status=400)

    for campo in _CAMPOS_ETAPA:
        if campo not in body:
            return JsonResponse({'detail': f'Campo obrigatório ausente: {campo}.'}, status=400)

    try:
        novo_prazo = date.fromisoformat(body['prazo']) if body['prazo'] else None
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'prazo inválido (esperado AAAA-MM-DD).'}, status=400)
    if novo_prazo is None:
        return JsonResponse({'detail': 'prazo é obrigatório.'}, status=400)

    usuario, erro = _buscar_usuario(usuario_uuid)
    if erro:
        return erro

    try:
        etapa = Etapa.objects.select_related('auditoria').get(id_unico=id_unico)
    except (Etapa.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({'detail': 'Etapa não encontrada.'}, status=404)

    if not usuario.tem_permissao('auditorias', 'editar'):
        return JsonResponse({'detail': 'Perfil sem permissão para editar etapas.'}, status=403)
    if not etapa.auditoria.usuarios_envolvidos.filter(pk=usuario.pk).exists():
        return JsonResponse({'detail': 'Usuário não está envolvido na auditoria desta etapa.'}, status=403)

    dados_atuais = _campos_etapa_para_comparacao(etapa)
    if baseline != dados_atuais:
        ultimo_historico = (
            HistoricoAlteracoes.objects
            .filter(tipo_objeto='Etapa', uuid_objeto=etapa.id_unico)
            .order_by('-data_hora_alteracao')
            .first()
        )
        usuario_atual = ultimo_historico.usuario if ultimo_historico else None
        resolvedor = determinar_resolvedor(etapa.auditoria, usuario, usuario_atual)
        novos = {campo: body[campo] for campo in _CAMPOS_ETAPA}
        conflito = ConflitoEtapa.objects.create(
            etapa=etapa,
            usuario_originador=usuario,
            dados_originador=novos,
            usuario_atual=usuario_atual,
            dados_atuais=dados_atuais,
            atribuido_a=resolvedor,
        )
        return JsonResponse(
            {'detail': 'conflito_pendente', 'conflito_id': str(conflito.id_unico)},
            status=409,
        )

    with set_current_user(usuario):
        etapa.orientacao = body['orientacao']
        etapa.documentos = body['documentos']
        etapa.atividade = body['atividade']
        etapa.prazo = novo_prazo
        etapa.situacao = body['situacao']
        etapa.metodo = body['metodo']
        etapa.save()

    return JsonResponse(_serializar_etapa(etapa))


@csrf_exempt
@requer_chave_interna
@require_POST
def api_mobile_excluir_etapa(request, id_unico):
    """
    Idempotente: se a etapa já não existe (retry após um sucesso cuja
    resposta se perdeu), devolve sucesso em vez de 404. RBAC usa a ação
    'excluir' (diferente de 'editar', mesma distinção que o próprio site
    já faz em crud_Auditoria_views.excluir_etapa).
    """
    from ..models import Etapa

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Corpo da requisição inválido.'}, status=400)

    usuario_uuid = body.get('usuario_uuid')
    if not usuario_uuid:
        return JsonResponse({'detail': 'usuario_uuid é obrigatório.'}, status=400)

    usuario, erro = _buscar_usuario(usuario_uuid)
    if erro:
        return erro

    try:
        etapa = Etapa.objects.select_related('auditoria').get(id_unico=id_unico)
    except (Etapa.DoesNotExist, ValueError, ValidationError):
        return JsonResponse({'id_unico': str(id_unico), 'ja_excluida': True})

    if not usuario.tem_permissao('auditorias', 'excluir'):
        return JsonResponse({'detail': 'Perfil sem permissão para excluir etapas.'}, status=403)
    if not etapa.auditoria.usuarios_envolvidos.filter(pk=usuario.pk).exists():
        return JsonResponse({'detail': 'Usuário não está envolvido na auditoria desta etapa.'}, status=403)

    with set_current_user(usuario):
        etapa.delete()

    return JsonResponse({'id_unico': str(id_unico), 'ja_excluida': False})
