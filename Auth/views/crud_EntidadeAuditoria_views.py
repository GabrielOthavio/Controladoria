from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao, get_per_page
from ..forms import EntidadeAuditoriaForm
from ..models import EntidadeAuditoria


@login_required(login_url='Auth:login')
def lista_entidades(request):
    per_page = get_per_page(request)
    q = request.GET.get('q', '').strip()
    qs = EntidadeAuditoria.objects.order_by('nome')
    if q:
        qs = qs.filter(nome__icontains=q)
    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'entidade_auditoria/lista.html', {
        'entidades':   page_obj,
        'page_obj':    page_obj,
        'paginator':   paginator,
        'per_page':    per_page,
        'q':           q,
        'extra_query': '',
    })


@login_required(login_url='Auth:login')
@requer_permissao('entidades', 'criar')
def adicionar_entidade(request):
    if request.method == 'POST':
        form = EntidadeAuditoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entidade cadastrada com sucesso!')
            return redirect('Auth:lista_entidades')
    else:
        form = EntidadeAuditoriaForm()
    return render(request, 'entidade_auditoria/formulario.html', {'form': form, 'titulo': 'Nova Entidade'})


@login_required(login_url='Auth:login')
@requer_permissao('entidades', 'editar')
def editar_entidade(request, id_unico):
    entidade = get_object_or_404(EntidadeAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        form = EntidadeAuditoriaForm(request.POST, instance=entidade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entidade atualizada com sucesso!')
            return redirect('Auth:lista_entidades')
    else:
        form = EntidadeAuditoriaForm(instance=entidade)
    return render(request, 'entidade_auditoria/formulario.html', {'form': form, 'titulo': f'Editando: {entidade.nome}'})


@login_required(login_url='Auth:login')
@requer_permissao('entidades', 'excluir')
def excluir_entidade(request, id_unico):
    entidade = get_object_or_404(EntidadeAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        entidade.delete()
        messages.success(request, 'Entidade excluída com sucesso!')
        return redirect('Auth:lista_entidades')
    return render(request, 'entidade_auditoria/confirmar_exclusao.html', {'objeto': entidade})
