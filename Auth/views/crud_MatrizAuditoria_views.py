from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import MatrizAuditoriaForm
from ..models import MatrizAuditoria


@login_required(login_url='Auth:login')
def lista_matrizes(request):
    matrizes = MatrizAuditoria.objects.order_by('pk')
    return render(request, 'matriz_auditoria/lista.html', {'matrizes': matrizes})


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
