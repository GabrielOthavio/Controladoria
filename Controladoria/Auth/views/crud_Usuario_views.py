# ===============================================
# ==            CRUDS PARA USUÁRIO            ==
# ===============================================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib import messages

from ..forms import UsuarioForm
from ..models import Usuario
from .Core_views import is_chefe

@login_required(login_url='Auth:login')
def lista_usuarios(request):
    """Lista todos os usuários. Acessível apenas para CHEFES."""
    usuarios = Usuario.objects.all().order_by('first_name')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def adicionar_usuario(request):
    """
    Processa o formulário para adicionar um novo Usuário.
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário adicionado com sucesso!')
            return redirect('Auth:lista_usuarios')
    else:
        form = UsuarioForm()
    context = {'form': form, 'titulo': 'Adicionar Usuário'}
    return render(request, 'usuarios/formulario.html', context)

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def editar_usuario(request, id_unico):
    """
    Processa o formulário para editar um Usuário existente.
    """
    usuario = get_object_or_404(Usuario, id_unico=id_unico)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('Auth:lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    context = {'form': form, 'titulo': f'Editando "{usuario.get_full_name() or usuario.username}"'}
    return render(request, 'usuarios/formulario.html', context)

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def excluir_usuario(request, id_unico):
    """
    Exibe a confirmação e processa a exclusão de um Usuário.
    """
    usuario = get_object_or_404(Usuario, id_unico=id_unico)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('Auth:lista_usuarios')
    context = {'objeto': usuario}
    return render(request, 'usuarios/confirmar_exclusao.html', context)