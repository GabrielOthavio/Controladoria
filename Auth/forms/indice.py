import bleach
from django import forms
from ..models import Indice, TipoIndice, GrupoIndice
from .utils import ALLOWED_TAGS


class IndiceForm(forms.ModelForm):
    class Meta:
        model = Indice
        fields = ['tipo_indice', 'mes', 'ano', 'valor', 'observacao']
        widgets = {
            'tipo_indice': forms.Select(attrs={'class': 'form-select'}),
            'mes':         forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'ano':         forms.NumberInput(attrs={'class': 'form-control', 'min': 2000}),
            'valor':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'observacao':  forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_ano(self):
        import datetime
        ano = self.cleaned_data.get('ano')
        if ano and ano > datetime.date.today().year + 5:
            raise forms.ValidationError(f"O ano não pode ser superior a {datetime.date.today().year + 5}.")
        return ano

    def clean_observacao(self):
        value = self.cleaned_data.get('observacao') or ''
        return bleach.clean(value, tags=ALLOWED_TAGS, strip=True) or None


class TipoIndiceForm(forms.ModelForm):
    class Meta:
        model = TipoIndice
        fields = ['descricao', 'indice_grupo', 'observacao']
        widgets = {
            'descricao':    forms.TextInput(attrs={'class': 'form-control'}),
            'indice_grupo': forms.Select(attrs={'class': 'form-select'}),
            'observacao':   forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_descricao(self):
        return bleach.clean(self.cleaned_data.get('descricao', ''), tags=[], strip=True)

    def clean_observacao(self):
        return bleach.clean(self.cleaned_data.get('observacao', ''), tags=ALLOWED_TAGS, strip=True)


class GrupoIndiceForm(forms.ModelForm):
    class Meta:
        model = GrupoIndice
        fields = ['nome', 'observacao']
        widgets = {
            'nome':       forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_nome(self):
        return bleach.clean(self.cleaned_data.get('nome', ''), tags=[], strip=True)

    def clean_observacao(self):
        return bleach.clean(self.cleaned_data.get('observacao', ''), tags=ALLOWED_TAGS, strip=True)
