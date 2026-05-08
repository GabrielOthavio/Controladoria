from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import EntidadeAuditoriaForm
from ..models import EntidadeAuditoria


@login_required(login_url='Auth:login')
def lista_entidades(request):
    try:
        per_page = int(request.GET.get('per_page', 16))
        if per_page not in (8, 16, 32, 64):
            per_page = 16
    except (ValueError, TypeError):
        per_page = 16
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
def adicionar_entidade(request):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem cadastrar entidades.")
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
def editar_entidade(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem editar entidades.")
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
def excluir_entidade(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem excluir entidades.")
    entidade = get_object_or_404(EntidadeAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        entidade.delete()
        messages.success(request, 'Entidade excluída com sucesso!')
        return redirect('Auth:lista_entidades')
    return render(request, 'entidade_auditoria/confirmar_exclusao.html', {'objeto': entidade})
