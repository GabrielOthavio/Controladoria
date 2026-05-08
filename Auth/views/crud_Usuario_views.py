# ===============================================
# ==            CRUDS PARA USUÁRIO            ==
# ===============================================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib import messages

from ..forms import AdminUserCreationForm, CustomUserChangeForm
from ..models import Usuario
from .Core_views import is_chefe

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def lista_usuarios(request):
    try:
        per_page = int(request.GET.get('per_page', 16))
        if per_page not in (8, 16, 32, 64):
            per_page = 16
    except (ValueError, TypeError):
        per_page = 16
    q = request.GET.get('q', '').strip()
    qs = Usuario.objects.all().order_by('first_name')
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(username__icontains=q)  | Q(email__icontains=q)
        )
    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'usuarios/lista.html', {
        'usuarios':    page_obj,
        'page_obj':    page_obj,
        'paginator':   paginator,
        'per_page':    per_page,
        'q':           q,
        'extra_query': '',
    })

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def adicionar_usuario(request):
    """
    Processa o formulário para adicionar um novo Usuário.
    """
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário adicionado com sucesso!')
            return redirect('Auth:lista_usuarios')
    else:
        form = AdminUserCreationForm()
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
        form = CustomUserChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('Auth:lista_usuarios')
    else:
        form = CustomUserChangeForm(instance=usuario)
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