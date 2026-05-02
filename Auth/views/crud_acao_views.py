# ===============================================
# ==            CRUD PARA AÇÕES              ==
# ===============================================
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import AcaoForm
from ..models import Acao, TipoAcao


@login_required(login_url='Auth:login')
def lista_acoes(request):
    acoes = Acao.objects.select_related('tipo_acao', 'usuario').order_by('-data_execucao')
    context = {'acoes': acoes}
    return render(request, 'acoes/lista.html', context)


@login_required(login_url='Auth:login')
def adicionar_acao(request):
    if request.method == 'POST':
        form = AcaoForm(request.POST)
        if form.is_valid():
            acao = form.save(commit=False)
            acao.usuario = request.user
            acao.save()
            messages.success(request, 'Ação cadastrada com sucesso!')
            return redirect('Auth:lista_acoes')
    else:
        form = AcaoForm()
    tipos_acao_json = list(TipoAcao.objects.values('id', 'mensagem_padrao_avaliacao', 'mensagem_padrao_conclusao'))
    context = {'form': form, 'tipos_acao_json': tipos_acao_json, 'titulo': 'Adicionar Nova Ação'}
    return render(request, 'acoes/formulario.html', context)


@login_required(login_url='Auth:login')
def editar_acao(request, id_unico):
    acao = get_object_or_404(Acao, id_unico=id_unico)
    if acao.usuario != request.user and request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Você não tem permissão para editar esta ação.")
    if request.method == 'POST':
        form = AcaoForm(request.POST, instance=acao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ação atualizada com sucesso!')
            return redirect('Auth:lista_acoes')
    else:
        form = AcaoForm(instance=acao)
    tipos_acao_json = list(TipoAcao.objects.values('id', 'mensagem_padrao_avaliacao', 'mensagem_padrao_conclusao'))
    context = {'form': form, 'tipos_acao_json': tipos_acao_json, 'titulo': f'Editando: {acao.identificacao_semantica}'}
    return render(request, 'acoes/formulario.html', context)


@login_required(login_url='Auth:login')
def excluir_acao(request, id_unico):
    acao = get_object_or_404(Acao, id_unico=id_unico)
    if acao.usuario != request.user and request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Você não tem permissão para excluir esta ação.")
    if request.method == 'POST':
        acao.delete()
        messages.success(request, 'Ação excluída com sucesso!')
        return redirect('Auth:lista_acoes')
    context = {'objeto': acao}
    return render(request, 'acoes/confirmar_exclusao.html', context)