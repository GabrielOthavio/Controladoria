from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from ..forms import CustomUserCreationForm
from django.urls import reverse_lazy
from ..models import Usuario, Acao, Auditoria

def register(request):
    """View para registrar um novo usuário (pode ser pública ou restrita)."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso! Por favor, faça o login.')
            return redirect('Auth:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def is_chefe(user):
    """
    Verifica se o usuário logado tem o perfil 'CHEFE'.
    """
    return user.is_authenticated and user.perfil == 'CHEFE'

@login_required(login_url='Auth:login')
def dashboard(request):
    """Página principal do sistema após o usuário fazer login."""
    context = {
        'total_acoes': Acao.objects.count(),
        'total_auditorias': Auditoria.objects.count(),
        'total_usuarios': Usuario.objects.count(),
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def lista_usuarios(request):
    """Lista todos os usuários. Acessível para TODOS os perfis logados."""
    usuarios = Usuario.objects.all().order_by('first_name')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})