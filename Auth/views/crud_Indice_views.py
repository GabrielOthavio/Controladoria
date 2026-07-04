# ===============================================
# ==              CRUD PARA ÍNDICES            ==
# ===============================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao, get_per_page
from ..forms import IndiceForm
from ..models import Indice

@login_required(login_url='Auth:login')
@requer_permissao('indices', 'ver')
def lista_indices(request):
    per_page = get_per_page(request)
    q = request.GET.get('q', '').strip()
    qs = Indice.objects.select_related('tipo_indice').order_by('-ano', '-mes')
    if q:
        qs = qs.filter(Q(tipo_indice__descricao__icontains=q) | Q(observacao__icontains=q))
    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    context = {
        'indices':     page_obj,
        'page_obj':    page_obj,
        'paginator':   paginator,
        'per_page':    per_page,
        'q':           q,
        'extra_query': '',
    }
    return render(request, 'indices/lista.html', context)

@login_required(login_url='Auth:login')
@requer_permissao('indices', 'criar')
def adicionar_indice(request):
    """ Processa o formulário para adicionar um novo Índice. """
    if request.method == 'POST':
        form = IndiceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Índice cadastrado com sucesso!')
                return redirect('Auth:lista_indices')
            except Exception as e:
                messages.error(request, f'Erro ao salvar índice: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = IndiceForm()
    context = {'form': form,'titulo': 'Adicionar Novo Índice'}
    return render(request, 'indices/formulario.html', context)

@login_required(login_url='Auth:login')
@requer_permissao('indices', 'editar')
def editar_indice(request, id_unico):
    """ Processa o formulário para editar um Índice existente. """
    indice = get_object_or_404(Indice, id_unico=id_unico)
    if request.method == 'POST':
        form = IndiceForm(request.POST, instance=indice)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Índice atualizado com sucesso!')
                return redirect('Auth:lista_indices')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar índice: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = IndiceForm(instance=indice)
    context = {'form': form,'titulo': f'Editando Índice: {indice.tipo_indice.descricao} ({indice.mes}/{indice.ano})'}
    return render(request, 'indices/formulario.html', context)


@login_required(login_url='Auth:login')
@requer_permissao('indices', 'excluir')
def excluir_indice(request, id_unico):
    """ Exibe a confirmação e processa a exclusão de um Índice. """
    indice = get_object_or_404(Indice, id_unico=id_unico)
    if request.method == 'POST':
        indice.delete()
        messages.success(request, 'Índice excluído com sucesso!')
        return redirect('Auth:lista_indices')
    context = {'objeto': indice}
    return render(request, 'indices/confirmar_exclusao.html', context)
