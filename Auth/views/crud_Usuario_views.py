# ===============================================
# ==            CRUDS PARA USUÁRIO            ==
# ===============================================

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from ..decorators import requer_permissao, get_per_page
from ..forms import AdminUserCreationForm, CustomUserChangeForm
from ..models import Usuario

@login_required(login_url='Auth:login')
@requer_permissao('usuarios', 'ver')
def lista_usuarios(request):
    per_page = get_per_page(request)
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
@requer_permissao('usuarios', 'criar')
def adicionar_usuario(request):
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
@requer_permissao('usuarios', 'editar')
def editar_usuario(request, id_unico):
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
@requer_permissao('usuarios', 'excluir')
def excluir_usuario(request, id_unico):
    usuario = get_object_or_404(Usuario, id_unico=id_unico)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('Auth:lista_usuarios')
    context = {'objeto': usuario}
    return render(request, 'usuarios/confirmar_exclusao.html', context)
