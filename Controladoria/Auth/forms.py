import bleach
from django import forms
import datetime
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Usuario,
    TipoAcao,
    TipoIndice,
    Acao,
    Indice,
    Auditoria,
    ConfiguracaoSistema,
    GrupoIndice,
)

# Lista de tags HTML seguras permitidas em campos de texto. Pode ser vazia para não permitir nenhuma.
ALLOWED_TAGS = ['b', 'i', 'u', 'p', 'br']

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulário de autenticação customizado para aplicar estilos do Bootstrap.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nome de Usuário'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Senha'}
        )

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Segurança: listando campos explicitamente para evitar mass assignment.
        fields = (
            'username', 'first_name', 'last_name', 'email', 'cpf', 'telefone',
            'rua', 'bairro', 'numero', 'cep', 'perfil'
        )
class CustomUserChangeForm(UserChangeForm):
    """
    Formulário para editar usuários existentes, baseado no modelo customizado.
    """
    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name', 'cpf', 'telefone',
            'rua', 'bairro', 'numero', 'cep', 'perfil', 'is_active', 'is_staff'
        )
class TipoAcaoForm(forms.ModelForm):
    class Meta:
        model = TipoAcao
        # Segurança: listando campos explicitamente.
        fields = ['nome_tipo_acao', 'motivo_tipo_acao', 'mensagem_padrao_avaliacao', 'mensagem_padrao_conclusao']

        widgets = {
            'nome_tipo_acao': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo_tipo_acao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'mensagem_padrao_avaliacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'mensagem_padrao_conclusao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    def clean_nome_tipo_acao(self):
        data = self.cleaned_data['nome_tipo_acao']
        return bleach.clean(data, tags=[], strip=True)

    def clean_motivo_tipo_acao(self):
        data = self.cleaned_data['motivo_tipo_acao']
        return bleach.clean(data, tags=ALLOWED_TAGS, strip=True)

class AcaoForm(forms.ModelForm):
    data_execucao = forms.DateField(
        label="Data de Execução",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        initial=datetime.date.today
    )
    class Meta:
        model = Acao
        fields = ['data_execucao', 'tipo_acao', 'numero_acao', 'avaliacao', 'conclusao']
        widgets = {
            'tipo_acao': forms.Select(attrs={'class': 'form-select'}),
            'avaliacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'conclusao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero_acao'].required = False
        self.fields['numero_acao'].widget.attrs['readonly'] = True
        self.fields['numero_acao'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        instance = super().save(commit=commit)

        if not instance.numero_acao:
            instance.numero_acao = instance.id
            if commit:
                instance.save(update_fields=['numero_acao'])
        return instance
class IndiceForm(forms.ModelForm):
    class Meta:
        model = Indice
        fields = ['tipo_indice', 'mes', 'ano', 'observacao']

    def clean_observacao(self):
        data = self.cleaned_data['observacao']
        return bleach.clean(data, tags=ALLOWED_TAGS, strip=True)

ALLOWED_TAGS = ['b', 'i', 'u', 'p', 'br', 'strong', 'em', 'li', 'ul', 'ol']

class TipoIndiceForm(forms.ModelForm):
    class Meta:
        model = TipoIndice
        fields = ['nome_tipo_indice', 'indice_grupo', 'observacao']
        # Esta seção garante que os campos tenham a classe 'form-control' do Bootstrap
        widgets = {
            'nome_tipo_indice': forms.TextInput(attrs={'class': 'form-control'}),
            'indice_grupo': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    # Limpa o campo 'nome_tipo_indice', removendo TODAS as tags HTML
    def clean_nome_tipo_indice(self):
        data = self.cleaned_data.get('nome_tipo_indice', '')
        return bleach.clean(data, tags=[], strip=True)

    # Limpa o campo 'observacao', permitindo apenas as tags seguras listadas em ALLOWED_TAGS
    def clean_observacao(self):
        data = self.cleaned_data.get('observacao', '')
        return bleach.clean(data, tags=ALLOWED_TAGS, strip=True)
    
class AuditoriaForm(forms.ModelForm):
    class Meta:
        model = Auditoria
        # Segurança: Usar 'fields' é mais seguro que 'exclude'.
        fields = ['nome_auditoria', 'etapas', 'usuarios_envolvidos', 'informacoes_campos_texto']
        widgets = {
            'usuarios_envolvidos': forms.CheckboxSelectMultiple,
        }

    def clean_nome_auditoria(self):
        data = self.cleaned_data['nome_auditoria']
        return bleach.clean(data, tags=[], strip=True)

    def clean_etapas(self):
        data = self.cleaned_data['etapas']
        return bleach.clean(data, tags=ALLOWED_TAGS, strip=True)
    
    def clean_informacoes_campos_texto(self):
        data = self.cleaned_data['informacoes_campos_texto']
        return bleach.clean(data, tags=ALLOWED_TAGS, strip=True)

class GerarRelatorioForm(forms.Form):
    TIPO_RELATORIO_CHOICES = [
        ('AUDITORIA', 'Auditorias'),
        ('ACAO', 'Ações'),
        ('INDICE', 'Índices'),
    ]
    nome_relatorio = forms.CharField(label="Nome do Relatório", max_length=255)
    tipo_relatorio = forms.ChoiceField(label="Tipo de Relatório", choices=TIPO_RELATORIO_CHOICES)
    data_inicio = forms.DateField(label="Data de Início", widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(label="Data de Fim", widget=forms.DateInput(attrs={'type': 'date'}))

    # Validação de segurança e integridade
    def clean_nome_relatorio(self):
        data = self.cleaned_data['nome_relatorio']
        return bleach.clean(data, tags=[], strip=True)

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_fim = cleaned_data.get("data_fim")

        if data_inicio and data_fim:
            if data_fim < data_inicio:
                raise forms.ValidationError("A data final não pode ser anterior à data inicial.")
        return cleaned_data
    
class GrupoIndiceForm(forms.ModelForm):
    """
    Formulário para criar e editar Grupos de Índice.
    """
    class Meta:
        model = GrupoIndice
        fields = ['nome_grupo_indice', 'observacao']
        widgets = {
            'nome_grupo_indice': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_nome_grupo_indice(self):
        """ Higieniza o campo 'nome_grupo_indice', removendo todas as tags HTML. """
        data = self.cleaned_data.get('nome_grupo_indice', '')
        return bleach.clean(data, tags=[], strip=True)

    def clean_observacao(self):
        """ Higieniza o campo 'observacao', permitindo apenas tags seguras. """
        data = self.cleaned_data.get('observacao', '')
        # Reutilizando a lista de tags seguras já definida no seu arquivo
        return bleach.clean(data, tags=ALLOWED_TAGS, strip=True)