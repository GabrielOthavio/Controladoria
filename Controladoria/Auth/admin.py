from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario,
    TipoAcao,
    TipoIndice,
    Acao,
    Indice,
    Auditoria,
    HistoricoAlteracoes,
    LogAcesso,
    ConfiguracaoSistema,
    Relatorio
)

# Customiza a exibição do seu modelo de usuário
class CustomUserAdmin(UserAdmin):
    model = Usuario
    # Adiciona 'perfil' aos campos exibidos e editáveis no admin
    fieldsets = UserAdmin.fieldsets + (
        ('Dados Customizados', {'fields': ('perfil', 'cpf', 'telefone', 'rua', 'bairro', 'numero', 'cep')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados Customizados', {'fields': ('perfil', 'cpf', 'telefone')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'perfil', 'is_staff')
    list_filter = ('perfil', 'is_staff', 'is_active')

@admin.register(TipoAcao)
class TipoAcaoAdmin(admin.ModelAdmin):
    list_display = ('nome_acao', 'motivo_acao')
    search_fields = ('nome_acao',)

@admin.register(TipoIndice)
class TipoIndiceAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'indice_grupo')
    search_fields = ('descricao',)

@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = ('tipo_acao', 'data_execucao', 'numero_acao')
    list_filter = ('data_execucao', 'tipo_acao')

@admin.register(Indice)
class IndiceAdmin(admin.ModelAdmin):
    list_display = ('tipo_indice', 'mes', 'ano')
    list_filter = ('tipo_indice', 'ano')

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_auditoria', 'data_criacao')
    filter_horizontal = ('usuarios_envolvidos',)

@admin.register(HistoricoAlteracoes)
class HistoricoAlteracoesAdmin(admin.ModelAdmin):
    list_display = ('tipo_objeto', 'id_objeto', 'usuario', 'data_hora_alteracao')
    list_filter = ('tipo_objeto', 'data_hora_alteracao')
    # Torna o admin somente leitura, pois os registros são criados pelo sistema
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_hora_acesso', 'ip_acesso')
    list_filter = ('data_hora_acesso',)
    # Torna o admin somente leitura
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'descricao')

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('nome_relatorio', 'data_geracao')
    # Torna o admin somente leitura
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

# Registra o modelo de usuário customizado
admin.site.register(Usuario, CustomUserAdmin)