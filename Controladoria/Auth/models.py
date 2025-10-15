import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from encrypted_model_fields.fields import EncryptedCharField
import datetime
class Usuario(AbstractUser):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    PERFIL_CHOICES = (('CHEFE', 'Chefe'), ('FUNCIONARIO', 'Funcionário'))
    cpf = EncryptedCharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=15, blank=True, null=True)
    rua = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    perfil = models.CharField(max_length=11, choices=PERFIL_CHOICES, default='FUNCIONARIO')
    def __str__(self):
        return self.get_full_name() or self.username
class TipoAcao(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_tipo_acao = models.CharField(max_length=255, verbose_name="Nome da Ação", unique=True)
    motivo_tipo_acao = models.TextField(verbose_name="Motivo da Ação")
    mensagem_padrao_avaliacao = models.TextField(verbose_name="Mensagem Padrão para Avaliação", blank=True, null=True)
    mensagem_padrao_conclusao = models.TextField(verbose_name="Mensagem Padrão para Conclusão", blank=True, null=True)
    def __str__(self):
        return self.nome_tipo_acao

class GrupoIndice(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_grupo_indice = models.CharField(max_length=150, unique=True, verbose_name="Nome do Grupo",help_text="Nome único para o grupo de índice.")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    class Meta:
        verbose_name = "Grupo de Índice"
        verbose_name_plural = "Grupos de Índices"
        ordering = ['nome_grupo_indice']
    def __str__(self):
        return self.nome_grupo_indice
    
class TipoIndice(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_tipo_indice = models.CharField(max_length=255, verbose_name="nome tipo indice", null=True) # Allow null values
    indice_grupo = models.ForeignKey(GrupoIndice, on_delete=models.PROTECT, verbose_name="Grupo do Índice")    
    observacao = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.nome_tipo_indice

class Acao(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data_execucao = models.DateField(verbose_name="Data de Execução")
    tipo_acao = models.ForeignKey(TipoAcao, on_delete=models.PROTECT, verbose_name="Tipo de Ação")
    numero_acao = models.IntegerField(verbose_name="Número da Ação", null=True, blank=True)
    avaliacao = models.TextField()
    conclusao = models.TextField()

    def __str__(self):
        return f"{self.tipo_acao.nome_tipo_acao} - {self.data_execucao}"

class Indice(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tipo_indice = models.ForeignKey(TipoIndice, on_delete=models.PROTECT, verbose_name="Tipo de Índice")
    mes = models.IntegerField(verbose_name="Mês", validators=[MinValueValidator(1), MaxValueValidator(12)])
    ano = models.IntegerField(verbose_name="Ano", validators=[MinValueValidator(2000), MaxValueValidator(datetime.date.today().year + 5)])
    valor = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    class Meta:
        unique_together = ('tipo_indice', 'mes', 'ano')
    def __str__(self):
        return f"{self.tipo_indice.nome_tipo_indice} - {self.mes}/{self.ano}"

class Auditoria(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_auditoria = models.CharField(max_length=255, verbose_name="Nome da Auditoria")
    etapas = models.TextField(verbose_name="Etapas da Auditoria")
    usuarios_envolvidos = models.ManyToManyField(Usuario, verbose_name="Usuários Envolvidos")
    informacoes_campos_texto = models.TextField(verbose_name="Informações dos Campos de Texto")
    data_criacao = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nome_auditoria
    
class HistoricoAlteracoes(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    data_hora_alteracao = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora da Alteração")
    tipo_objeto = models.CharField(max_length=100, verbose_name="Tipo do Objeto")
    id_objeto = models.PositiveIntegerField(verbose_name="ID do Objeto")
    descricao_alteracao = models.TextField(verbose_name="Descrição da Alteração")
    def __str__(self):
        user_display = self.usuario.username if self.usuario else 'Sistema'
        return f"[{user_display}] alterou [{self.tipo_objeto} ID: {self.id_objeto}] em {self.data_hora_alteracao.strftime('%d/%m/%Y %H:%M')}"

# Lógica de Sinais para auditoria automática
@receiver(post_save)
def log_alteracoes(sender, instance, created, **kwargs):
    """
    Este sinal é chamado sempre que um objeto é salvo e cria um registro
    de auditoria no HistoricoAlteracoes.
    """
    modelos_auditaveis = [Usuario, TipoAcao, TipoIndice, Acao, Indice, Auditoria]
    if sender not in modelos_auditaveis:
        return
    acao = "CRIADO" if created else "ATUALIZADO"
    descricao = f"Objeto {sender.__name__} com ID {instance.pk} foi {acao}."
    HistoricoAlteracoes.objects.create(
        tipo_objeto=sender.__name__,
        id_objeto=instance.pk,
        descricao_alteracao=descricao
    )

class LogAcesso(models.Model):
    """
    Registra os logs de acesso dos usuários (Entidade Operacional).
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuário")
    data_hora_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora do Acesso")
    ip_acesso = models.GenericIPAddressField(verbose_name="IP de Acesso")
    def __str__(self):
        return f"{self.usuario.username} - {self.data_hora_acesso}"
    
class ConfiguracaoSistema(models.Model):
    """
    Armazena as configurações do sistema (Entidade de Configuração).
    """
    chave = models.CharField(max_length=100, unique=True, verbose_name="Chave de Configuração")
    valor = models.TextField(verbose_name="Valor da Configuração")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    def __str__(self):
        return self.chave

class Relatorio(models.Model):
    id_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    """
    Armazena os relatórios gerados no sistema (Entidade de Configuração).
    """
    nome_relatorio = models.CharField(max_length=255, verbose_name="Nome do Relatório")
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    conteudo = models.TextField(verbose_name="Conteúdo do Relatório")
    def __str__(self):
        return self.nome_relatorio