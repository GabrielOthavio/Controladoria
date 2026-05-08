from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import MatrizAuditoriaForm
from ..models import MatrizAuditoria


@login_required(login_url='Auth:login')
def lista_matrizes(request):
    try:
        per_page = int(request.GET.get('per_page', 16))
        if per_page not in (8, 16, 32, 64):
            per_page = 16
    except (ValueError, TypeError):
        per_page = 16
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
def adicionar_matriz(request):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem cadastrar matrizes.")
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
def editar_matriz(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem editar matrizes.")
    matriz = get_object_or_404(MatrizAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        form = MatrizAuditoriaForm(request.POST, instance=matriz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matriz de auditoria atualizada com sucesso!')
            return redirect('Auth:lista_matrizes')
    else:
        form = MatrizAuditoriaForm(instance=matriz)
    return render(request, 'matriz_auditoria/formulario.html', {'form': form, 'titulo': f'Editando Matriz #{matriz.pk}'})


@login_required(login_url='Auth:login')
def excluir_matriz(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem excluir matrizes.")
    matriz = get_object_or_404(MatrizAuditoria, id_unico=id_unico)
    if request.method == 'POST':
        matriz.delete()
        messages.success(request, 'Matriz de auditoria excluída com sucesso!')
        return redirect('Auth:lista_matrizes')
    return render(request, 'matriz_auditoria/confirmar_exclusao.html', {'objeto': matriz})
