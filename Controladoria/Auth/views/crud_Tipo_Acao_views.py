# ===============================================
# ==            CRUDS PARA TIPO AÇÃO           ==
# ===============================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from ..forms import TipoAcaoForm
from ..models import TipoAcao
from .Core_views import is_chefe

@login_required(login_url='Auth:login')
def lista_tipos_acao(request):
    """Lista todos os Tipos de Ação cadastrados."""
    tipos_acao = TipoAcao.objects.all()
    return render(request, 'tipos_acao/lista.html', {'tipos_acao': tipos_acao})

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def adicionar_tipo_acao(request):
    """Adiciona um novo Tipo de Ação."""
    if request.method == 'POST':
        form = TipoAcaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Ação cadastrado com sucesso!')
            return redirect('Auth:lista_tipos_acao')
    else:
        form = TipoAcaoForm()
    return render(request, 'tipos_acao/formulario.html', {'form': form, 'titulo': 'Adicionar Tipo de Ação'})

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def editar_tipo_acao(request, id_unico):
    """Edita um Tipo de Ação existente."""
    tipo_acao = get_object_or_404(TipoAcao, id_unico=id_unico)
    if request.method == 'POST':
        form = TipoAcaoForm(request.POST, instance=tipo_acao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Ação atualizado com sucesso!')
            return redirect('Auth:lista_tipos_acao')
    else:
        form = TipoAcaoForm(instance=tipo_acao)
    return render(request, 'tipos_acao/formulario.html', {'form': form, 'titulo': f'Editando "{tipo_acao.nome_acao}"'})

@login_required(login_url='Auth:login')
@user_passes_test(is_chefe, login_url=reverse_lazy('Auth:dashboard'))
def excluir_tipo_acao(request, id_unico):
    """Exclui um Tipo de Ação."""
    # ... (lógica da view continua a mesma)
    tipo_acao = get_object_or_404(TipoAcao, id_unico=id_unico)
    if request.method == 'POST':
        try:
            tipo_acao.delete()
            messages.success(request, 'Tipo de Ação excluído com sucesso!')
        except Exception:
            messages.error(request, 'Não foi possível excluir, pois este item está em uso.')
        return redirect('Auth:lista_tipos_acao')
    return render(request, 'tipos_acao/confirmar_exclusao.html', {'objeto': tipo_acao})