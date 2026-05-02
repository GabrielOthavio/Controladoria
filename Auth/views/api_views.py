from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models import Count


@login_required(login_url='Auth:login')
@require_GET
def api_dashboard(request):
    from ..models import Auditoria, Acao, Indice, Usuario
    status_counts = (
        Auditoria.objects
        .values('status')
        .annotate(total=Count('status'))
        .order_by('status')
    )
    return JsonResponse({
        'total_acoes':      Acao.objects.count(),
        'total_auditorias': Auditoria.objects.count(),
        'total_indices':    Indice.objects.count(),
        'total_usuarios':   Usuario.objects.count(),
        'auditorias_por_status': list(status_counts),
    })


@login_required(login_url='Auth:login')
@require_GET
def api_historico(request):
    from ..models import HistoricoAlteracoes
    limit = min(int(request.GET.get('limit', 20)), 100)
    qs = (
        HistoricoAlteracoes.objects
        .select_related('usuario')
        .order_by('-data_hora_alteracao')[:limit]
    )
    results = [
        {
            'id':          str(h.id_unico),
            'usuario':     (h.usuario.get_full_name() or h.usuario.username) if h.usuario else 'Sistema',
            'tipo_objeto': h.tipo_objeto,
            'operacao':    h.operacao,
            'uuid_objeto': str(h.uuid_objeto) if h.uuid_objeto else None,
            'data_hora':   h.data_hora_alteracao.strftime('%d/%m/%Y %H:%M'),
        }
        for h in qs
    ]
    return JsonResponse({'results': results})


@login_required(login_url='Auth:login')
@require_GET
def api_auditorias(request):
    from ..models import Auditoria
    qs = Auditoria.objects.all().order_by('-data_criacao')[:50]
    results = [
        {
            'id':            str(a.id_unico),
            'nome':          a.nome_auditoria,
            'status':        a.status,
            'data_inicio':   a.data_inicio.strftime('%d/%m/%Y') if a.data_inicio else None,
            'data_conclusao': a.data_conclusao.strftime('%d/%m/%Y') if a.data_conclusao else None,
            'apuracao_inicial': str(a.apuracao_inicial) if a.apuracao_inicial is not None else None,
            'apuracao_final':   str(a.apuracao_final)   if a.apuracao_final   is not None else None,
            'resultado_calculado': str(a.resultado_calculado) if a.resultado_calculado is not None else None,
        }
        for a in qs
    ]
    return JsonResponse({'results': results})


@login_required(login_url='Auth:login')
@require_GET
def api_acoes(request):
    from ..models import Acao
    qs = Acao.objects.select_related('tipo_acao', 'usuario').order_by('-data_execucao')[:50]
    results = [
        {
            'id':            str(a.id_unico),
            'identificacao': a.identificacao_semantica,
            'tipo_acao':     a.tipo_acao.nome_acao,
            'usuario':       a.usuario.get_full_name() or a.usuario.username,
            'data_execucao': a.data_execucao.strftime('%d/%m/%Y'),
        }
        for a in qs
    ]
    return JsonResponse({'results': results})
