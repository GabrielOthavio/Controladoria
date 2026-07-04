
# ===============================================
# ==        CRUD PARA GRUPOS DE ÍNDICE        ==
# ===============================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao, get_per_page
from ..forms import GrupoIndiceForm
from ..models import GrupoIndice


@login_required(login_url='Auth:login')
@requer_permissao('grupos_indice', 'ver')
def lista_grupos_indice(request):
    per_page = get_per_page(request)
    q = request.GET.get('q', '').strip()
    qs = GrupoIndice.objects.all().order_by('nome')
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(observacao__icontains=q))
    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    context = {
        'grupos_indice': page_obj,
        'page_obj':      page_obj,
        'paginator':     paginator,
        'per_page':      per_page,
        'q':             q,
        'extra_query':   '',
    }
    return render(request, 'grupos_indice/lista.html', context)

@login_required(login_url='Auth:login')
@requer_permissao('grupos_indice', 'criar')
def adicionar_grupo_indice(request):
    if request.method == 'POST':
        form = GrupoIndiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo de Índice cadastrado com sucesso!')
            return redirect('Auth:lista_grupos_indice')
    else:
        form = GrupoIndiceForm()
    context = {'form': form, 'titulo': 'Adicionar Novo Grupo de Índice'}
    return render(request, 'grupos_indice/formulario.html', context)


@login_required(login_url='Auth:login')
@requer_permissao('grupos_indice', 'editar')
def editar_grupo_indice(request, id_unico):
    grupo = get_object_or_404(GrupoIndice, id_unico=id_unico)
    if request.method == 'POST':
        form = GrupoIndiceForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect('Auth:lista_grupos_indice')
    else:
        form = GrupoIndiceForm(instance=grupo)

    context = {'form': form, 'titulo': f'Editando Grupo "{grupo.nome}"'}
    return render(request, 'grupos_indice/formulario.html', context)


@login_required(login_url='Auth:login')
@requer_permissao('grupos_indice', 'excluir')
def excluir_grupo_indice(request, id_unico):
    grupo = get_object_or_404(GrupoIndice, id_unico=id_unico)
    if request.method == 'POST':
        try:
            grupo.delete()
            messages.success(request, 'Grupo de Índice excluído com sucesso!')
        except Exception:
            messages.error(request, 'Não foi possível excluir, pois este grupo está em uso.')
        return redirect('Auth:lista_grupos_indice')

    context = {'objeto': grupo}
    return render(request, 'grupos_indice/confirmar_exclusao.html', context)
