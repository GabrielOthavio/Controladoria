from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao
from ..models import Perfil, PerfilPermissao, TELA_CHOICES

_SECOES = [
    ('Visão Geral',   ['dashboard']),
    ('Operacional',   ['acoes', 'indices', 'auditorias', 'matrizes', 'entidades']),
    ('Configuração',  ['tipos_acao', 'tipos_indice', 'grupos_indice']),
    ('Administração', ['usuarios', 'perfis']),
]


def _telas_secoes():
    label = dict(TELA_CHOICES)
    return [
        {'secao': s, 'telas': [(c, label[c]) for c in codes if c in label]}
        for s, codes in _SECOES
    ]


def _resolve_parent_pk(parent_str):
    if not parent_str:
        return None
    try:
        return Perfil.objects.get(id_unico=parent_str).pk
    except (Perfil.DoesNotExist, ValueError, ValidationError):
        return None


def _build_tree(perfis, parent_id=None, depth=0):
    result = []
    for p in perfis:
        if p.parent_id == parent_id:
            result.append({'perfil': p, 'depth': depth})
            result.extend(_build_tree(perfis, p.id, depth + 1))
    return result


@login_required(login_url='Auth:login')
@requer_permissao('perfis', 'ver')
def lista_perfis(request):
    q = request.GET.get('q', '').strip()
    qs = list(Perfil.objects.prefetch_related('permissoes').select_related('parent'))

    if q:
        qs_filtrado = [p for p in qs if q.lower() in p.nome.lower() or q.lower() in p.descricao.lower()]
        tree = [{'perfil': p, 'depth': 0} for p in qs_filtrado]
    else:
        tree = _build_tree(qs)

    return render(request, 'perfis/lista.html', {
        'tree':  tree,
        'telas': TELA_CHOICES,
        'q':     q,
        'total': len(qs),
    })


@login_required(login_url='Auth:login')
@requer_permissao('perfis', 'criar')
def adicionar_perfil(request):
    if request.method == 'POST':
        nome      = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        parent_id = _resolve_parent_pk(request.POST.get('parent'))
        if not nome:
            messages.error(request, 'O nome do perfil é obrigatório.')
            return render(request, 'perfis/formulario.html', {
                'titulo': 'Novo Perfil',
                'telas_secoes': _telas_secoes(),
                'perfis_disponiveis': Perfil.objects.all(),
                'perms': {},
            })
        perfil = Perfil.objects.create(nome=nome, descricao=descricao, parent_id=parent_id)
        _salvar_permissoes(perfil, request.POST)
        messages.success(request, f'Perfil "{perfil.nome}" criado com sucesso!')
        return redirect('Auth:lista_perfis')

    return render(request, 'perfis/formulario.html', {
        'titulo': 'Novo Perfil',
        'telas_secoes': _telas_secoes(),
        'perfis_disponiveis': Perfil.objects.all(),
        'perms': {},
    })


@login_required(login_url='Auth:login')
@requer_permissao('perfis', 'editar')
def editar_perfil(request, id_unico):
    perfil = get_object_or_404(Perfil, id_unico=id_unico)
    perms  = {p.tela: p for p in perfil.permissoes.all()}
    descendentes = _get_descendentes(perfil)
    perfis_disponiveis = Perfil.objects.exclude(pk__in=descendentes).exclude(pk=perfil.pk)

    if request.method == 'POST':
        nome      = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        parent_id = _resolve_parent_pk(request.POST.get('parent'))
        if not nome:
            messages.error(request, 'O nome do perfil é obrigatório.')
        elif parent_id and (parent_id == perfil.pk or parent_id in descendentes):
            messages.error(request, 'Um perfil não pode ser pai de si mesmo ou de um de seus descendentes.')
        else:
            perfil.nome      = nome
            perfil.descricao = descricao
            perfil.parent_id = parent_id
            perfil.save()
            _salvar_permissoes(perfil, request.POST)
            messages.success(request, f'Perfil "{perfil.nome}" atualizado com sucesso!')
            return redirect('Auth:lista_perfis')

    return render(request, 'perfis/formulario.html', {
        'titulo': f'Editando: {perfil.nome}',
        'perfil': perfil,
        'telas_secoes': _telas_secoes(),
        'perms':  perms,
        'perfis_disponiveis': perfis_disponiveis,
    })


@login_required(login_url='Auth:login')
@requer_permissao('perfis', 'excluir')
def excluir_perfil(request, id_unico):
    perfil = get_object_or_404(Perfil, id_unico=id_unico)
    if request.method == 'POST':
        if perfil.usuarios.exists():
            messages.error(request, f'Não é possível excluir: {perfil.usuarios.count()} usuário(s) possuem este perfil.')
            return redirect('Auth:lista_perfis')
        if perfil.filhos.exists():
            messages.error(request, f'Não é possível excluir: este perfil possui {perfil.filhos.count()} perfil(is) filho(s).')
            return redirect('Auth:lista_perfis')
        nome = perfil.nome
        perfil.delete()
        messages.success(request, f'Perfil "{nome}" excluído.')
        return redirect('Auth:lista_perfis')

    return render(request, 'perfis/confirmar_exclusao.html', {'objeto': perfil})


def _salvar_permissoes(perfil, post):
    for tela, _ in TELA_CHOICES:
        perm, _ = PerfilPermissao.objects.get_or_create(perfil=perfil, tela=tela)
        novo_ver     = bool(post.get(f'{tela}_ver'))
        novo_criar   = bool(post.get(f'{tela}_criar'))
        novo_editar  = bool(post.get(f'{tela}_editar'))
        novo_excluir = bool(post.get(f'{tela}_excluir'))
        if (perm.pode_ver, perm.pode_criar, perm.pode_editar, perm.pode_excluir) == \
           (novo_ver, novo_criar, novo_editar, novo_excluir):
            continue
        perm.pode_ver     = novo_ver
        perm.pode_criar   = novo_criar
        perm.pode_editar  = novo_editar
        perm.pode_excluir = novo_excluir
        perm.save()


def _get_descendentes(perfil):
    ids = set()
    queue = list(perfil.filhos.values_list('pk', flat=True))
    while queue:
        pk = queue.pop()
        if pk not in ids:
            ids.add(pk)
            queue.extend(Perfil.objects.filter(parent_id=pk).values_list('pk', flat=True))
    return ids
