# ===============================================
# ==         CRUDS PARA TIPO DE ÍNDICE         ==
# ===============================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao, get_per_page
from ..forms import TipoIndiceForm
from ..models import TipoIndice

@login_required(login_url='Auth:login')
@requer_permissao('tipos_indice', 'ver')
def lista_tipos_indice(request):
    per_page = get_per_page(request)
    q = request.GET.get('q', '').strip()
    qs = TipoIndice.objects.select_related('indice_grupo').order_by('descricao')
    if q:
        qs = qs.filter(Q(descricao__icontains=q) | Q(indice_grupo__nome__icontains=q))
    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    context = {
        'tipos_indice': page_obj,
        'page_obj':     page_obj,
        'paginator':    paginator,
        'per_page':     per_page,
        'q':            q,
        'extra_query':  '',
    }
    return render(request, 'tipos_indice/lista.html', context)


@login_required(login_url='Auth:login')
@requer_permissao('tipos_indice', 'criar')
def adicionar_tipo_indice(request):
    if request.method == 'POST':
        form = TipoIndiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Índice cadastrado com sucesso!')
            return redirect('Auth:lista_tipos_indice')
    else:
        form = TipoIndiceForm()
    context = {'form': form, 'titulo': 'Adicionar Tipo de Índice'}
    return render(request, 'tipos_indice/formulario.html', context)


@login_required(login_url='Auth:login')
@requer_permissao('tipos_indice', 'editar')
def editar_tipo_indice(request, id_unico):
    tipo_indice = get_object_or_404(TipoIndice, id_unico=id_unico)
    if request.method == 'POST':
        form = TipoIndiceForm(request.POST, instance=tipo_indice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Índice atualizado com sucesso!')
            return redirect('Auth:lista_tipos_indice')
    else:
        form = TipoIndiceForm(instance=tipo_indice)
    context = {'form': form, 'titulo': f'Editando "{tipo_indice.descricao}"'}
    return render(request, 'tipos_indice/formulario.html', context)

@login_required(login_url='Auth:login')
@requer_permissao('tipos_indice', 'excluir')
def excluir_tipo_indice(request, id_unico):
    tipo_indice = get_object_or_404(TipoIndice, id_unico=id_unico)
    if request.method == 'POST':
        try:
            tipo_indice.delete()
            messages.success(request, 'Tipo de Índice excluído com sucesso!')
        except Exception:
            messages.error(request, 'Não foi possível excluir, pois este tipo está em uso.')
        return redirect('Auth:lista_tipos_indice')
    context = {'objeto': tipo_indice}
    return render(request, 'tipos_indice/confirmar_exclusao.html', context)
