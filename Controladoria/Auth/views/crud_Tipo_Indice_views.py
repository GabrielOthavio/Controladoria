# ===============================================
# ==         CRUDS PARA TIPO DE ÍNDICE         ==
# ===============================================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from ..forms import TipoIndiceForm
from ..models import TipoIndice
from .Core_views import is_chefe

@login_required(login_url='Auth:login')
def lista_tipos_indice(request):
    """
    Exibe uma lista de todos os Tipos de Índice cadastrados.
    """
    tipos_indice = TipoIndice.objects.all().order_by('nome_tipo_indice')
    context = {'tipos_indice': tipos_indice}
    return render(request, 'tipos_indice/lista.html', context)


@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def adicionar_tipo_indice(request):
    """
    Processa o formulário para adicionar um novo Tipo de Índice.
    """
    if request.method == 'POST':
        form = TipoIndiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Auth:lista_tipos_indice')
    else:
        form = TipoIndiceForm()
    context = {'form': form,'titulo': 'Adicionar Tipo de Índice'}
    return render(request, 'tipos_indice/formulario.html', context)


@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def editar_tipo_indice(request, id_unico):
    """
    Processa o formulário para editar um Tipo de Índice existente.
    """
    tipo_indice = get_object_or_404(TipoIndice, id_unico=id_unico)
    if request.method == 'POST':
        form = TipoIndiceForm(request.POST, instance=tipo_indice)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Tipo de Índice atualizado com sucesso!')
            return redirect('Auth:lista_tipos_indice')
    else:
        form = TipoIndiceForm(instance=tipo_indice)
    context = {'form': form,'titulo': f'Editando "{tipo_indice.nome_tipo_indice}"'}
    return render(request, 'tipos_indice/formulario.html', context)

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def excluir_tipo_indice(request, id_unico):
    """
    Exibe a confirmação e processa a exclusão de um Tipo de Índice.
    """
    tipo_indice = get_object_or_404(TipoIndice, id_unico=id_unico)
    if request.method == 'POST':
        tipo_indice.delete()
        return redirect('Auth:lista_tipos_indice')
    context = {'objeto': tipo_indice}
    return render(request, 'tipos_indice/confirmar_exclusao.html', context)