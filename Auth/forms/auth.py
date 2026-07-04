from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from ..models import Usuario, Perfil
from .utils import validate_cpf


class CustomAuthenticationForm(AuthenticationForm):
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
        fields = (
            'username', 'first_name', 'last_name', 'email', 'cpf',
            'telefone', 'rua', 'bairro', 'numero', 'cep', 'unidade',
        )
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX.XXX.XXX-XX'}),
            'telefone':   forms.TextInput(attrs={'class': 'form-control'}),
            'rua':        forms.TextInput(attrs={'class': 'form-control'}),
            'bairro':     forms.TextInput(attrs={'class': 'form-control'}),
            'numero':     forms.TextInput(attrs={'class': 'form-control'}),
            'cep':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXXX-XXX'}),
            'unidade':    forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_cpf(self):
        return validate_cpf(self.cleaned_data.get('cpf', ''))


class AdminUserCreationForm(CustomUserCreationForm):
    """Formulário de criação de usuário exclusivo para admins — inclui campo perfil."""
    perfil = forms.ModelChoiceField(
        queryset=Perfil.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Perfil',
        required=True,
    )

    class Meta(CustomUserCreationForm.Meta):
        fields = CustomUserCreationForm.Meta.fields + ('perfil',)


class CustomUserChangeForm(UserChangeForm):
    password = None  # oculta o hash de senha do formulário de edição
    perfil = forms.ModelChoiceField(
        queryset=Perfil.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Perfil',
        required=True,
    )

    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name', 'cpf',
            'telefone', 'rua', 'bairro', 'numero', 'cep', 'unidade', 'perfil', 'is_active',
        )
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'cpf':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX.XXX.XXX-XX'}),
            'telefone':   forms.TextInput(attrs={'class': 'form-control'}),
            'rua':        forms.TextInput(attrs={'class': 'form-control'}),
            'bairro':     forms.TextInput(attrs={'class': 'form-control'}),
            'numero':     forms.TextInput(attrs={'class': 'form-control'}),
            'cep':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXXX-XXX'}),
            'unidade':    forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cpf(self):
        return validate_cpf(self.cleaned_data.get('cpf', ''))
