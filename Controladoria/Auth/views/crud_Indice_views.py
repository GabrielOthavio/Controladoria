# ===============================================
# ==              CRUD PARA ÍNDICES            ==
# ===============================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from ..forms import IndiceForm
from ..models import Indice
from .Core_views import is_chefe

@login_required(login_url='Auth:login')
def lista_indices(request):
    """ Exibe uma lista de todos os Índices cadastrados. """
    indices = Indice.objects.all().order_by('-ano', '-mes') # Mais recentes primeiro
    context = {'indices': indices}
    return render(request, 'indices/lista.html', context)

@login_required(login_url='Auth:login')
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
    context = {'form': form,'titulo': f'Editando Índice: {indice.tipo_indice.nome_tipo_indice} ({indice.mes}/{indice.ano})'}
    return render(request, 'indices/formulario.html', context)


@login_required(login_url='Auth:login')
def excluir_indice(request, id_unico):
    """ Exibe a confirmação e processa a exclusão de um Índice. """
    indice = get_object_or_404(Indice, id_unico=id_unico)
    if request.method == 'POST':
        indice.delete()
        messages.success(request, 'Índice excluído com sucesso!')
        return redirect('Auth:lista_indices')
    context = {'objeto': indice}
    return render(request, 'indices/confirmar_exclusao.html', context)