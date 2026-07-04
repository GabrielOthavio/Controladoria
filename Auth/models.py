import uuid
from decimal import Decimal
from uuid import UUID as _UUID
from datetime import date, datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.functional import cached_property
from encrypted_model_fields.fields import EncryptedCharField


# ---------------------------------------------------------------------------
# RBAC — Perfis e Permissões
# ---------------------------------------------------------------------------

TELA_CHOICES = [
    ('dashboard',     'Dashboard'),
    ('acoes',         'Ações'),
    ('indices',       'Índices'),
    ('tipos_acao',    'Tipos de Ação'),
    ('tipos_indice',  'Tipos de Índice'),
    ('grupos_indice', 'Grupos de Índice'),
    ('auditorias',    'Auditorias'),
    ('matrizes',      'Matrizes de Auditoria'),
    ('entidades',     'Entidades de Auditoria'),
    ('usuarios',      'Usuários'),
    ('perfis',        'Perfis'),
]


class Perfil(models.Model):
    id_unico  = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome      = models.CharField(max_length=100, unique=True, verbose_name='Nome')
    descricao = models.TextField(blank=True, default='', verbose_name='Descrição')
    parent    = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='filhos',
        verbose_name='Perfil Pai',
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @cached_property
    def _permissoes_dict(self):
        return {p.tela: p for p in self.permissoes.all()}

    def tem_permissao(self, tela, acao='ver'):
        perm = self._permissoes_dict.get(tela)
        return bool(getattr(perm, f'pode_{acao}', False)) if perm else False

    def profundidade(self):
        depth, current, visitados = 0, self, {self.pk}
        while current.parent_id and current.parent_id not in visitados:
            depth += 1
            visitados.add(current.parent_id)
            current = current.parent
        return depth


class PerfilPermissao(models.Model):
    perfil       = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='permissoes')
    tela         = models.CharField(max_length=30, choices=TELA_CHOICES, verbose_name='Tela')
    pode_ver     = models.BooleanField(default=False, verbose_name='Ver')
    pode_criar   = models.BooleanField(default=False, verbose_name='Criar')
    pode_editar  = models.BooleanField(default=False, verbose_name='Editar')
    pode_excluir = models.BooleanField(default=False, verbose_name='Excluir')

    class Meta:
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'
        unique_together = ('perfil', 'tela')

    def __str__(self):
        return f'{self.perfil.nome} → {self.get_tela_display()}'


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

class Usuario(AbstractUser):
    id_unico  = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cpf       = EncryptedCharField(max_length=14, unique=True, verbose_name="CPF")
    telefone  = models.CharField(max_length=15, blank=True, null=True)
    rua       = models.CharField(max_length=255, blank=True, null=True)
    bairro    = models.CharField(max_length=100, blank=True, null=True)
    numero    = models.CharField(max_length=10, blank=True, null=True)
    cep       = models.CharField(max_length=9, blank=True, null=True)
    perfil    = models.ForeignKey(
        'Perfil', on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name='Perfil', related_name='usuarios'
    )

    def tem_permissao(self, tela, acao='ver'):
        if not self.perfil_id:
            return False
        return self.perfil.tem_permissao(tela, acao)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def iniciais(self):
        nome = self.get_full_name()
        if nome:
            partes = nome.split()
            if len(partes) >= 2:
                return (partes[0][0] + partes[-1][0]).upper()
            return partes[0][:2].upper()
        return self.username[:2].upper()


class TipoAcao(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_acao = models.CharField(max_length=255, verbose_name="Nome da Ação", unique=True)
    motivo_acao = models.TextField(verbose_name="Motivo da Ação")
    mensagem_padrao_avaliacao = models.TextField(verbose_name="Mensagem Padrão para Avaliação", blank=True, null=True)
    mensagem_padrao_conclusao = models.TextField(verbose_name="Mensagem Padrão para Conclusão", blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Ação"
        verbose_name_plural = "Tipos de Ação"
        ordering = ['nome_acao']

    def __str__(self):
        return self.nome_acao


class GrupoIndice(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=150, unique=True, verbose_name="Nome do Grupo", help_text="Nome único para o grupo de índice.")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    class Meta:
        verbose_name = "Grupo de Índice"
        verbose_name_plural = "Grupos de Índices"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class TipoIndice(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    indice_grupo = models.ForeignKey(GrupoIndice, on_delete=models.PROTECT, verbose_name="Grupo do Índice")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    class Meta:
        verbose_name = "Tipo de Índice"
        verbose_name_plural = "Tipos de Índice"
        ordering = ['descricao']
        unique_together = ('descricao', 'indice_grupo')

    def __str__(self):
        return self.descricao


class Acao(models.Model):
    STATUS_CHOICES = [
        ('EM_ANDAMENTO',      'Em andamento'),
        ('AGUARDANDO_REVISAO','Aguardando revisão'),
        ('HOMOLOGADA',        'Homologada'),
        ('ATRASADA',          'Atrasada'),
    ]
    UNIDADE_CHOICES = [
        ('SEFAZ',  'SEFAZ'),
        ('SESAU',  'SESAU'),
        ('SEINFRA','SEINFRA'),
        ('SEMA',   'SEMA'),
        ('SEAD',   'SEAD'),
        ('SEDUC',  'SEDUC'),
        ('SESP',   'SESP'),
        ('SEAG',   'SEAG'),
        ('SEJEL',  'SEJEL'),
        ('SEDU',   'SEDU'),
        ('OUTRO',  'Outro'),
    ]

    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    id_por_tipo_acao = models.PositiveIntegerField(editable=False, verbose_name="Ref. Categoria")
    data_execucao = models.DateField(verbose_name="Data de Execução")
    tipo_acao = models.ForeignKey('TipoAcao', on_delete=models.PROTECT, verbose_name="Tipo de Ação")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Responsável")
    avaliacao = models.TextField(verbose_name="Avaliação")
    conclusao = models.TextField(verbose_name="Conclusão")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EM_ANDAMENTO', verbose_name="Status")
    unidade = models.CharField(max_length=20, choices=UNIDADE_CHOICES, default='SEFAZ', verbose_name="Unidade")
    is_paint = models.BooleanField(default=False, verbose_name="PAINT")

    class Meta:
        unique_together = ['tipo_acao', 'id_por_tipo_acao']
        verbose_name = "Ação"
        verbose_name_plural = "Ações"

    def save(self, *args, **kwargs):
        if not self.id_por_tipo_acao:
            from django.db import transaction
            with transaction.atomic():
                TipoAcao.objects.select_for_update().get(pk=self.tipo_acao_id)
                ultimo = (
                    Acao.objects.select_for_update()
                    .filter(tipo_acao=self.tipo_acao)
                    .order_by('-id_por_tipo_acao')
                    .first()
                )
                self.id_por_tipo_acao = (ultimo.id_por_tipo_acao + 1) if ultimo else 1
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    @property
    def identificacao_semantica(self):
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        mes_nome = meses[self.data_execucao.month - 1]
        return f"{self.tipo_acao.nome_acao} - {mes_nome}/{self.data_execucao.year} (Ref: {self.id_por_tipo_acao:03d})"

    def __str__(self):
        return self.identificacao_semantica


class Indice(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tipo_indice = models.ForeignKey(TipoIndice, on_delete=models.PROTECT, verbose_name="Tipo de Índice")
    mes = models.IntegerField(verbose_name="Mês", validators=[MinValueValidator(1), MaxValueValidator(12)])
    ano = models.IntegerField(verbose_name="Ano", validators=[MinValueValidator(2000)])
    valor = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Valor (%)", default=0)
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")

    class Meta:
        verbose_name = "Índice"
        verbose_name_plural = "Índices"
        ordering = ['-ano', '-mes']
        unique_together = ('tipo_indice', 'mes', 'ano')

    def __str__(self):
        return f"{self.tipo_indice.descricao} - {self.mes}/{self.ano}"


class EntidadeAuditoria(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome da Entidade")

    class Meta:
        verbose_name = "Entidade de Auditoria"
        verbose_name_plural = "Entidades de Auditoria"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class MatrizAuditoria(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    descricao = models.CharField(max_length=255, default='', verbose_name="Descrição/Nome da matriz de auditoria")
    objetivo = models.TextField(default='', verbose_name="Objetivo da matriz de auditoria")
    base_legal = models.CharField(max_length=500, default='', verbose_name="Base da matriz de auditoria")
    riscos = models.CharField(max_length=500, default='', verbose_name="Riscos da matriz de auditoria")
    criterios_indicadores = models.CharField(max_length=500, default='', verbose_name="Critérios Indicadores da matriz de auditoria")
    procedimentos = models.CharField(max_length=500, default='', verbose_name="Procedimentos da matriz de auditoria")
    conclusoes_esperadas = models.CharField(max_length=500, default='', verbose_name="Conclusões da matriz de auditoria")
    entidade = models.ForeignKey(
        EntidadeAuditoria, on_delete=models.PROTECT,
        null=True, blank=True, verbose_name="Entidade da matriz de auditoria"
    )
    observacoes = models.TextField(blank=True, default='', verbose_name="Observações adicionais da matriz de auditoria")
    class Meta:
        verbose_name = "Matriz de Auditoria"
        verbose_name_plural = "Matrizes de Auditoria"
        ordering = ['descricao']

    def __str__(self):
        return self.descricao
class Auditoria(models.Model):
    STATUS_CHOICES = [
        ('PLANEJADA',    'Planejada'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA',    'Concluída'),
        ('CANCELADA',    'Cancelada'),
    ]

    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_auditoria = models.CharField(max_length=255, verbose_name="Nome da Auditoria")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANEJADA', verbose_name="Status")
    matriz = models.ForeignKey(
        MatrizAuditoria, on_delete=models.PROTECT,
        null=True, blank=True, verbose_name="Matriz de Auditoria"
    )
    orgao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Órgão")
    responsavel_orgao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Responsável do Órgão")
    usuarios_envolvidos = models.ManyToManyField(Usuario, blank=True, verbose_name="Usuários Envolvidos")
    informacoes_campos_texto = models.TextField(blank=True, default='', verbose_name="Informações dos Campos de Texto")

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_conclusao = models.DateField(null=True, blank=True, verbose_name="Data de Conclusão")

    apuracao_inicial = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True, verbose_name="Apuração Inicial (R$)"
    )
    apuracao_final = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True, blank=True, verbose_name="Apuração Final (R$)"
    )

    class Meta:
        verbose_name = "Auditoria"
        verbose_name_plural = "Auditorias"
        ordering = ['-data_criacao']

    @property
    def resultado_calculado(self):
        if self.apuracao_inicial is not None and self.apuracao_final is not None:
            return self.apuracao_final - self.apuracao_inicial
        return None

    def __str__(self):
        return self.nome_auditoria


class Etapa(models.Model):
    SITUACAO_CHOICES = [
        ('PENDENTE',     'Pendente'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA',    'Concluída'),
        ('REABERTA',     'Reaberta'),
    ]
    id_unico   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    auditoria  = models.ForeignKey(Auditoria, on_delete=models.CASCADE, related_name='etapas_list', verbose_name="Auditoria")
    orientacao = models.TextField(verbose_name="Orientação")
    documentos = models.TextField(blank=True, default='', verbose_name="Documentos")
    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Usuário")
    atividade  = models.CharField(max_length=500, verbose_name="Atividade")
    prazo      = models.DateField(verbose_name="Prazo")
    situacao   = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='PENDENTE', verbose_name="Situação")
    metodo     = models.CharField(max_length=255, blank=True, default='', verbose_name="Método")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Etapa"
        verbose_name_plural = "Etapas"
        ordering = ['prazo']

    def __str__(self):
        return f"{self.auditoria.nome_auditoria} — {self.atividade[:50]}"


class Achado(models.Model):
    id_unico     = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    etapa        = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='achados', verbose_name="Etapa")
    descricao    = models.TextField(verbose_name="Descrição do Achado")
    data_achado  = models.DateField(auto_now_add=True, verbose_name="Data do Achado")
    usuario      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Usuário")

    class Meta:
        verbose_name = "Achado"
        verbose_name_plural = "Achados"
        ordering = ['-data_achado']

    def __str__(self):
        return f"Achado — {self.etapa.atividade[:40]}"


class HistoricoAlteracoes(models.Model):
    OPERACAO_CHOICES = [
        ('CRIADO',      'Criado'),
        ('ATUALIZADO',  'Atualizado'),
        ('EXCLUIDO',    'Excluído'),
    ]

    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(
        'Usuario', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Usuário"
    )
    
    data_hora_alteracao = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora da Alteração")
    operacao = models.CharField(max_length=10, choices=OPERACAO_CHOICES, default='ATUALIZADO', verbose_name="Operação")
    tipo_objeto = models.CharField(max_length=100, verbose_name="Tipo do Objeto")
    uuid_objeto = models.UUIDField(null=True, blank=True, verbose_name="UUID do Objeto")
    estado_anterior = models.JSONField(null=True, blank=True, verbose_name="Estado Anterior")
    estado_posterior = models.JSONField(null=True, blank=True, verbose_name="Estado Posterior")

    class Meta:
        verbose_name = "Histórico de Alteração"
        verbose_name_plural = "Histórico de Alterações"
        ordering = ['-data_hora_alteracao']

    def __str__(self):
        user_display = self.usuario.username if self.usuario else 'Sistema'
        ts = self.data_hora_alteracao.strftime('%d/%m/%Y %H:%M')
        return f"[{user_display}] {self.operacao} [{self.tipo_objeto}] em {ts}"


class LogAcesso(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    data_hora_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora do Acesso")
    ip_acesso = models.GenericIPAddressField(verbose_name="IP de Acesso")

    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ['-data_hora_acesso']

    def __str__(self):
        user_display = self.usuario.username if self.usuario else 'Usuário removido'
        return f"{user_display} - {self.data_hora_acesso}"


class ConfiguracaoSistema(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave de Configuração")
    valor = models.TextField(verbose_name="Valor da Configuração")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"

    def __str__(self):
        return self.chave


class Relatorio(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_relatorio = models.CharField(max_length=255, verbose_name="Nome do Relatório")
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    conteudo = models.TextField(verbose_name="Conteúdo do Relatório")

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-data_geracao']

    def __str__(self):
        return self.nome_relatorio


# ---------------------------------------------------------------------------
# Audit by Design — §4.3 do TCC
# ---------------------------------------------------------------------------

MODELOS_AUDITAVEIS = [
    Usuario, Perfil, PerfilPermissao,
    TipoAcao, GrupoIndice, TipoIndice, Acao, Indice,
    EntidadeAuditoria, MatrizAuditoria, Auditoria, ConfiguracaoSistema,
    Etapa, Achado,
]


CAMPOS_SENSIVEIS = {'password', 'last_login', 'email', 'telefone', 'rua', 'bairro', 'numero', 'cep'}


def _serializar_instancia(instance):
    """
    Retorna um dict com os campos escalares do modelo.
    Campos EncryptedCharField e CAMPOS_SENSIVEIS são marcados como [PROTEGIDO]
    para não expor dados sensíveis no log de auditoria.
    """
    resultado = {}
    for field in instance._meta.concrete_fields:
        if isinstance(field, EncryptedCharField) or field.name in CAMPOS_SENSIVEIS:
            resultado[field.name] = '[PROTEGIDO]'
            continue
        value = field.value_from_object(instance)
        if isinstance(value, (date, datetime)):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = str(value)
        elif isinstance(value, _UUID):
            value = str(value)
        resultado[field.name] = value
    return resultado


@receiver(pre_save, dispatch_uid='auditoria_pre_save')
def _capturar_estado_anterior(sender, instance, **kwargs):
    if sender not in MODELOS_AUDITAVEIS:
        return
    if instance.pk:
        try:
            instance._auditoria_estado_anterior = _serializar_instancia(
                sender.objects.get(pk=instance.pk)
            )
        except sender.DoesNotExist:
            instance._auditoria_estado_anterior = None
    else:
        instance._auditoria_estado_anterior = None


@receiver(post_save, dispatch_uid='auditoria_post_save')
def _registrar_auditoria(sender, instance, created, **kwargs):
    if sender not in MODELOS_AUDITAVEIS:
        return
    estado_anterior = getattr(instance, '_auditoria_estado_anterior', None)
    estado_posterior = _serializar_instancia(instance)
    if not created and estado_anterior == estado_posterior:
        return
    from Auth.middleware import get_current_user
    usuario = get_current_user()
    HistoricoAlteracoes.objects.create(
        operacao='CRIADO' if created else 'ATUALIZADO',
        tipo_objeto=sender.__name__,
        uuid_objeto=getattr(instance, 'id_unico', None),
        estado_anterior=estado_anterior,
        estado_posterior=estado_posterior,
        usuario=usuario if usuario and getattr(usuario, 'is_authenticated', False) else None,
    )
