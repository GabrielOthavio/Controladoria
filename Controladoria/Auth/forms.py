import bleach
from django import forms
import datetime
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
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
class UsuarioForm(forms.ModelForm):
    """
    Formulário para criar e editar usuários.
    """
    # Campos de senha: opcionais na edição, obrigatórios na criação
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Deixe em branco para manter a senha atual."
    )
    password2 = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Repita a senha."
    )
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email', 'cpf', 'telefone',
            'rua', 'bairro', 'numero', 'cep', 'perfil'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'João'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Silva'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@email.com'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua das Flores'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Centro'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'perfil': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Na criação, as senhas devem ser informadas (tornamos required True)
        if not self.instance or not self.instance.pk:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].help_text = "Senha do novo usuário."
            self.fields['password2'].help_text = "Repita a senha do novo usuário."

    def clean_cpf(self):
        data = self.cleaned_data.get('cpf', '')
        return bleach.clean(data, tags=[], strip=True)
    
    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get('password1')
        pwd2 = cleaned_data.get('password2')
        is_creation = not (self.instance and self.instance.pk)

        # Regras: na criação, senha é obrigatória; na edição, somente se algum dos campos foi preenchido
        if is_creation:
            if not pwd1 or not pwd2:
                raise forms.ValidationError("Informe e confirme a senha.")
        else:
            # Se um foi preenchido, exigir ambos
            if (pwd1 and not pwd2) or (pwd2 and not pwd1):
                raise forms.ValidationError("Para alterar a senha, preencha os dois campos de senha.")

        # Se ambos existem (criação ou alteração), validar igualdade e regras de senha
        if pwd1 and pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError("As senhas não coincidem.")
            # Validar com os validadores do Django (comprimento, complexidade, semelhança com usuário, etc.)
            # Usamos uma referência de usuário para os validadores (instância atual ou pseudo-usuário na criação)
            try:
                user_for_validation = self.instance if (self.instance and self.instance.pk) else Usuario(
                    username=cleaned_data.get('username', ''),
                    email=cleaned_data.get('email', '')
                )
                validate_password(pwd1, user=user_for_validation)
            except forms.ValidationError as e:
                self.add_error('password1', e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd1 = self.cleaned_data.get('password1')
        pwd2 = self.cleaned_data.get('password2')
        # Define/atualiza a senha somente se foi informada e validada
        if pwd1 and pwd2 and pwd1 == pwd2:
            user.set_password(pwd1)
        if commit:
            user.save()
        return user

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
            'numero_acao': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'style': 'background-color: #e9ecef;'}),
            'avaliacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'conclusao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Extrai o request dos kwargs
        super().__init__(*args, **kwargs)
        self.fields['numero_acao'].required = False
        self.fields['numero_acao'].widget.attrs['readonly'] = True
        
        # Para novas instâncias, define o usuário automaticamente
        if not self.instance.pk and self.request and self.request.user:
            self.instance.usuario = self.request.user

    def save(self, commit=True):
        instance = super().save(commit=False)  # Não salva ainda
        
        if commit:
            instance.save()
            
            # Define numero_acao após salvar se não estiver definido
            if not instance.numero_acao:
                instance.numero_acao = instance.id
                instance.save(update_fields=['numero_acao'])
        
        return instance
class IndiceForm(forms.ModelForm):
    class Meta:
        model = Indice
        fields = ['tipo_indice', 'mes', 'ano', 'valor', 'observacao']
        widgets = {
            'tipo_indice': forms.Select(attrs={'class': 'form-control'}),
            'mes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '12', 'placeholder': 'Digite um mês (1-12)'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001', 'placeholder': 'R$ 0,00000'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define o ano atual como valor inicial se não estiver editando
        if not self.instance.pk:
            self.fields['ano'].initial = datetime.date.today().year

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