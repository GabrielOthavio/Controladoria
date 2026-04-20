
# ===============================================
# ==        CRUD PARA GRUPOS DE ÍNDICE        ==
# ===============================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from ..forms import GrupoIndiceForm
from ..models import GrupoIndice
from .Core_views import is_chefe


@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def lista_grupos_indice(request):
    """
    Exibe uma lista de todos os Grupos de Índice.
    Acessível apenas para o perfil 'CHEFE'.
    """
    grupos = GrupoIndice.objects.all()
    context = {'grupos_indice': grupos}
    return render(request, 'grupos_indice/lista.html', context)

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def adicionar_grupo_indice(request):
    """
    Processa o formulário para adicionar um novo Grupo de Índice.
    """
    if request.method == 'POST':
        form = GrupoIndiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Auth:lista_grupos_indice')
    else:
        form = GrupoIndiceForm()
    context = {'form': form, 'titulo': 'Adicionar Novo Grupo de Índice'}
    return render(request, 'grupos_indice/formulario.html', context)


@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def editar_grupo_indice(request, id_unico):
    """
    Processa o formulário para editar um Grupo de Índice existente.
    """
    grupo = get_object_or_404(GrupoIndice, id_unico=id_unico)
    if request.method == 'POST':
        form = GrupoIndiceForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect('Auth:lista_grupos_indice')
    else:
        form = GrupoIndiceForm(instance=grupo)
        
    context = {'form': form,'titulo': f'Editando Grupo "{grupo.nome_grupo_indice}"'}
    return render(request, 'grupos_indice/formulario.html', context)


@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def excluir_grupo_indice(request, id_unico):
    """
    Exibe a confirmação e processa a exclusão de um Grupo de Índice.
    """
    grupo = get_object_or_404(GrupoIndice, id_unico=id_unico)
    if request.method == 'POST':
        try:
            grupo.delete()
            messages.success(request, 'Grupo de Índice excluído com sucesso!')
        except Exception as e:
            messages.error(request, 'Não foi possível excluir, pois este grupo está em uso.')
        return redirect('Auth:lista_grupos_indice')
        
    context = {'objeto': grupo}
    return render(request, 'grupos_indice/confirmar_exclusao.html', context)
