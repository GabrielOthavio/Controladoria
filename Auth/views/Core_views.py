from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from ..forms import AdminUserCreationForm
from django.urls import reverse_lazy

def is_chefe(user):
    return user.is_authenticated and user.perfil == 'CHEFE'

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def register(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('Auth:lista_usuarios')
    else:
        form = AdminUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required(login_url='Auth:login')
def dashboard(request):
    return render(request, 'spa.html')
