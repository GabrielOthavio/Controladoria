from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import AuditoriaForm, EtapaForm, AchadoForm
from ..models import Auditoria, Etapa, Achado


@login_required(login_url='Auth:login')
def lista_auditorias(request):
    try:
        per_page = int(request.GET.get('per_page', 16))
        if per_page not in (8, 16, 32, 64):
            per_page = 16
    except (ValueError, TypeError):
        per_page = 16

    q             = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    qs_base = (
        Auditoria.objects
        .prefetch_related('usuarios_envolvidos')
        .annotate(total_achados=Count('etapas_list__achados', distinct=True))
    )
    if q:
        qs_base = qs_base.filter(
            Q(nome_auditoria__icontains=q) | Q(orgao__icontains=q)
        )

    tab_counts = {
        'total':        qs_base.count(),
        'planejada':    qs_base.filter(status='PLANEJADA').count(),
        'em_andamento': qs_base.filter(status='EM_ANDAMENTO').count(),
        'concluida':    qs_base.filter(status='CONCLUIDA').count(),
        'cancelada':    qs_base.filter(status='CANCELADA').count(),
    }

    qs = qs_base
    if status_filter:
        qs = qs.filter(status=status_filter)
    qs = qs.order_by('-data_criacao')

    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'auditorias/lista.html', {
        'auditorias':    page_obj,
        'page_obj':      page_obj,
        'paginator':     paginator,
        'per_page':      per_page,
        'q':             q,
        'status_filter': status_filter,
        'tab_counts':    tab_counts,
        'extra_query':   f'&status={status_filter}' if status_filter else '',
    })


@login_required(login_url='Auth:login')
def adicionar_auditoria(request):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem cadastrar auditorias.")
    if request.method == 'POST':
        form = AuditoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auditoria cadastrada com sucesso!')
            return redirect('Auth:lista_auditorias')
    else:
        form = AuditoriaForm()
    return render(request, 'auditorias/formulario.html', {'form': form, 'titulo': 'Nova Auditoria'})


@login_required(login_url='Auth:login')
def editar_auditoria(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem editar auditorias.")
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    if request.method == 'POST':
        form = AuditoriaForm(request.POST, instance=auditoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auditoria atualizada com sucesso!')
            return redirect('Auth:lista_auditorias')
    else:
        form = AuditoriaForm(instance=auditoria)
    return render(request, 'auditorias/formulario.html', {'form': form, 'titulo': f'Editando: {auditoria.nome_auditoria}'})


@login_required(login_url='Auth:login')
def excluir_auditoria(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem excluir auditorias.")
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    if request.method == 'POST':
        auditoria.delete()
        messages.success(request, 'Auditoria excluída com sucesso!')
        return redirect('Auth:lista_auditorias')
    return render(request, 'auditorias/confirmar_exclusao.html', {'objeto': auditoria})


# ── Gerenciar ──────────────────────────────────────────────────────────────────

@login_required(login_url='Auth:login')
def gerenciar_auditoria(request, id_unico):
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    etapas = (
        auditoria.etapas_list
        .select_related('usuario')
        .prefetch_related('achados')
        .all()
    )
    tab = request.GET.get('tab', 'etapas')
    return render(request, 'auditorias/gerenciar.html', {
        'auditoria': auditoria,
        'etapas': etapas,
        'tab': tab,
    })


# ── Etapas ─────────────────────────────────────────────────────────────────────

@login_required(login_url='Auth:login')
def adicionar_etapa(request, id_unico):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem adicionar etapas.")
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    if request.method == 'POST':
        form = EtapaForm(request.POST)
        if form.is_valid():
            etapa = form.save(commit=False)
            etapa.auditoria = auditoria
            etapa.save()
            messages.success(request, 'Etapa adicionada com sucesso!')
            return redirect('Auth:gerenciar_auditoria', id_unico=id_unico)
    else:
        form = EtapaForm(initial={'usuario': request.user})
    return render(request, 'auditorias/etapa_form.html', {
        'form': form,
        'auditoria': auditoria,
        'titulo': 'Adicionar Etapa',
    })


@login_required(login_url='Auth:login')
def editar_etapa(request, id_unico, etapa_id):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem editar etapas.")
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    etapa = get_object_or_404(Etapa, id_unico=etapa_id, auditoria=auditoria)
    achados = etapa.achados.select_related('usuario').all()
    achado_form = AchadoForm()

    if request.method == 'POST':
        action = request.POST.get('_action', 'etapa')
        if action == 'achado':
            achado_form = AchadoForm(request.POST)
            if achado_form.is_valid():
                achado = achado_form.save(commit=False)
                achado.etapa = etapa
                achado.usuario = request.user
                achado.save()
                messages.success(request, 'Achado registrado.')
                return redirect('Auth:editar_etapa', id_unico=id_unico, etapa_id=etapa_id)
        else:
            form = EtapaForm(request.POST, instance=etapa)
            if form.is_valid():
                form.save()
                messages.success(request, 'Etapa atualizada com sucesso!')
                return redirect('Auth:gerenciar_auditoria', id_unico=id_unico)
    else:
        form = EtapaForm(instance=etapa)

    return render(request, 'auditorias/etapa_form.html', {
        'form': form,
        'auditoria': auditoria,
        'etapa': etapa,
        'achados': achados,
        'achado_form': achado_form,
        'titulo': 'Editar Etapa',
    })


@login_required(login_url='Auth:login')
def excluir_etapa(request, id_unico, etapa_id):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden("Apenas chefes podem excluir etapas.")
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    etapa = get_object_or_404(Etapa, id_unico=etapa_id, auditoria=auditoria)
    if request.method == 'POST':
        etapa.delete()
        messages.success(request, 'Etapa excluída.')
        return redirect('Auth:gerenciar_auditoria', id_unico=id_unico)
    return render(request, 'auditorias/etapa_confirmar_exclusao.html', {
        'auditoria': auditoria,
        'etapa': etapa,
    })


@login_required(login_url='Auth:login')
def reabrir_etapa(request, id_unico, etapa_id):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden()
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    etapa = get_object_or_404(Etapa, id_unico=etapa_id, auditoria=auditoria)
    if request.method == 'POST':
        etapa.situacao = 'REABERTA'
        etapa.save()
        messages.success(request, 'Etapa reaberta.')
    return redirect('Auth:gerenciar_auditoria', id_unico=id_unico)


# ── Achados ────────────────────────────────────────────────────────────────────

@login_required(login_url='Auth:login')
def excluir_achado(request, id_unico, etapa_id, achado_id):
    if request.user.perfil != 'CHEFE':
        return HttpResponseForbidden()
    auditoria = get_object_or_404(Auditoria, id_unico=id_unico)
    etapa = get_object_or_404(Etapa, id_unico=etapa_id, auditoria=auditoria)
    achado = get_object_or_404(Achado, id_unico=achado_id, etapa=etapa)
    if request.method == 'POST':
        achado.delete()
        messages.success(request, 'Achado excluído.')
    return redirect('Auth:editar_etapa', id_unico=id_unico, etapa_id=etapa_id)
