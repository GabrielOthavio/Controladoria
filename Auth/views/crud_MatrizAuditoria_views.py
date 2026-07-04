from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao, get_per_page
from ..forms import MatrizAuditoriaForm
from ..models import MatrizAuditoria


@login_required(login_url='Auth:login')
@requer_permissao('matrizes', 'ver')
def lista_matrizes(request):
    per_page = get_per_page(request)
    q = request.GET.get('q', '').strip()
    qs = MatrizAuditoria.objects.select_related('entidade').order_by('pk')
    if q:
        qs = qs.filter(Q(descricao__icontains=q) | Q(entidade__nome__icontains=q))
    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'matriz_auditoria/lista.html', {
        'matrizes':    page_obj,
        'page_obj':    page_obj,
        'paginator':   paginator,
        'per_page':    per_page,
        'q':           q,
        'extra_query': '',
    })


@login_required(login_url='Auth:login')
@requer_permissao('matrizes', 'criar')
def adicionar_matriz(request):
    if request.method == 'POST':
        form = MatrizAuditoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matriz de auditoria cadastrada com sucesso!')
            return redirect('Auth:lista_matrizes')
    else:
        form = MatrizAuditoriaForm()
    return render(request, 'matriz_auditoria/formulario.html', {'form': form, 'titulo': 'Nova Matriz de Auditoria'})


@login_required(login_url='Auth:login')
@requer_permissao('matrizes', 'editar')
def editar_matriz(request, id_unico):
    matriz = get_object_or_404(MatrizAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        form = MatrizAuditoriaForm(request.POST, instance=matriz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matriz de auditoria atualizada com sucesso!')
            return redirect('Auth:lista_matrizes')
    else:
        form = MatrizAuditoriaForm(instance=matriz)
    return render(request, 'matriz_auditoria/formulario.html', {'form': form, 'titulo': f'Editando: {matriz.descricao}'})


@login_required(login_url='Auth:login')
@requer_permissao('matrizes', 'excluir')
def excluir_matriz(request, id_unico):
    matriz = get_object_or_404(MatrizAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        matriz.delete()
        messages.success(request, 'Matriz de auditoria excluída com sucesso!')
        return redirect('Auth:lista_matrizes')
    return render(request, 'matriz_auditoria/confirmar_exclusao.html', {'objeto': matriz})
