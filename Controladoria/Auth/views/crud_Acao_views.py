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
    """ Exibe uma lista de todas as Ações cadastradas. """
    acoes = Acao.objects.all().order_by('-data_execucao') # Mais recentes primeiro
    context = {'acoes': acoes}
    return render(request, 'acoes/lista.html', context)


@login_required(login_url='Auth:login')
def adicionar_acao(request):
    """ Processa o formulário para adicionar uma nova Ação. """
    if request.method == 'POST':
        form = AcaoForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ação cadastrada com sucesso!')
            return redirect('Auth:lista_acoes') 
    else:
        form = AcaoForm(request=request)
    tipos_acao_json = list(TipoAcao.objects.values('id', 'mensagem_padrao_avaliacao', 'mensagem_padrao_conclusao'))

    context = {'form': form,'tipos_acao_json': tipos_acao_json, 'titulo': 'Adicionar Nova Ação'}
    return render(request, 'acoes/acao_formulario.html', context)

@login_required(login_url='Auth:login')
def editar_acao(request, id_unico):
    """ Processa o formulário para editar uma Ação existente. """
    acao = get_object_or_404(Acao, id_unico=id_unico)
    # esse if faz com que apenas o usuario que cadastrou edite e exclua a ação
    if acao.usuario != request.user:
        return HttpResponseForbidden("Você não tem permissão para editar esta ação.")
    if request.method == 'POST':
        form = AcaoForm(request.POST, instance=acao, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ação atualizada com sucesso!')
            return redirect('Auth:lista_acoes')
    else:
        form = AcaoForm(instance=acao, request=request)
        
    # LINHA MODIFICADA: Prepara os dados para o JSON
    tipos_acao_json = list(TipoAcao.objects.values('id', 'mensagem_padrao_avaliacao', 'mensagem_padrao_conclusao'))
    context = {'form': form,'tipos_acao_json': tipos_acao_json,'titulo': f'Editando Ação #{acao.numero_acao}'}
    return render(request, 'acoes/acao_formulario.html', context)


@login_required(login_url='Auth:login')
def excluir_acao(request, id_unico):
    """ Exibe a confirmação e processa a exclusão de uma Ação. """
    acao = get_object_or_404(Acao, id_unico=id_unico)
    if request.method == 'POST':
        acao.delete()
        messages.success(request, 'Ação excluída com sucesso!')
        return redirect('Auth:lista_acoes')
    context = {'objeto': acao}
    return render(request, 'acoes/confirmar_exclusao.html', context)