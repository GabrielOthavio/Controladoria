# ===============================================
# ==            CRUD PARA AÇÕES              ==
# ===============================================
import csv
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import requer_permissao, get_per_page
from ..forms import AcaoForm
from ..models import Acao, TipoAcao


@login_required(login_url='Auth:login')
def lista_acoes(request):
    per_page = get_per_page(request)

    q       = request.GET.get('q', '').strip()
    tab     = request.GET.get('tab', 'todas')
    unidade = request.GET.get('unidade', '')
    sort    = request.GET.get('sort', '-data_execucao')
    if sort not in ('data_execucao', '-data_execucao'):
        sort = '-data_execucao'

    ano_atual = datetime.date.today().year

    qs_base = Acao.objects.select_related('tipo_acao', 'usuario')
    if q:
        qs_base = qs_base.filter(
            Q(tipo_acao__nome_acao__icontains=q) |
            Q(usuario__first_name__icontains=q) |
            Q(usuario__last_name__icontains=q) |
            Q(usuario__username__icontains=q) |
            Q(unidade__icontains=q)
        )
    if unidade:
        qs_base = qs_base.filter(unidade=unidade)

    tab_counts = qs_base.aggregate(
        total=Count('id'),
        paint=Count('id', filter=Q(is_paint=True)),
        em_andamento=Count('id', filter=Q(status='EM_ANDAMENTO')),
        aguardando_revisao=Count('id', filter=Q(status='AGUARDANDO_REVISAO')),
        homologadas=Count('id', filter=Q(status='HOMOLOGADA')),
        atrasadas=Count('id', filter=Q(status='ATRASADA')),
    )
    paint_ano = Acao.objects.filter(is_paint=True, data_execucao__year=ano_atual).count()

    qs = qs_base
    if tab == 'paint':
        qs = qs.filter(is_paint=True)
    elif tab == 'em_andamento':
        qs = qs.filter(status='EM_ANDAMENTO')
    elif tab == 'aguardando_revisao':
        qs = qs.filter(status='AGUARDANDO_REVISAO')
    elif tab == 'homologadas':
        qs = qs.filter(status='HOMOLOGADA')
    elif tab == 'atrasadas':
        qs = qs.filter(status='ATRASADA')

    qs = qs.order_by(sort)

    paginator = Paginator(qs, per_page)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    extra = f'&tab={tab}&sort={sort}'
    if unidade:
        extra += f'&unidade={unidade}'

    context = {
        'acoes':      page_obj,
        'page_obj':   page_obj,
        'paginator':  paginator,
        'per_page':   per_page,
        'q':          q,
        'tab':        tab,
        'unidade':    unidade,
        'sort':       sort,
        'tab_counts': tab_counts,
        'paint_ano':  paint_ano,
        'ano_atual':  ano_atual,
        'unidade_choices': Acao.UNIDADE_CHOICES,
        'extra_query': extra,
    }
    return render(request, 'acoes/lista.html', context)


@login_required(login_url='Auth:login')
@requer_permissao('acoes', 'ver')
def exportar_csv_acoes(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="acoes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Identificação', 'Tipo', 'Unidade', 'Data de Execução', 'Responsável', 'Status', 'PAINT'])
    qs = Acao.objects.select_related('tipo_acao', 'usuario').order_by('-data_execucao')
    for a in qs:
        writer.writerow([
            a.identificacao_semantica,
            a.tipo_acao.nome_acao,
            a.get_unidade_display(),
            a.data_execucao.strftime('%d/%m/%Y'),
            a.usuario.get_full_name() or a.usuario.username,
            a.get_status_display(),
            'Sim' if a.is_paint else 'Não',
        ])
    return response


@login_required(login_url='Auth:login')
@requer_permissao('acoes', 'criar')
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
    if acao.usuario != request.user and not request.user.tem_permissao('acoes', 'editar'):
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
    if acao.usuario != request.user and not request.user.tem_permissao('acoes', 'excluir'):
        return HttpResponseForbidden("Você não tem permissão para excluir esta ação.")
    if request.method == 'POST':
        acao.delete()
        messages.success(request, 'Ação excluída com sucesso!')
        return redirect('Auth:lista_acoes')
    context = {'objeto': acao}
    return render(request, 'acoes/confirmar_exclusao.html', context)
