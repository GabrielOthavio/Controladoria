import datetime
import bleach
from django import forms
from ..models import TipoAcao, Acao
from .utils import ALLOWED_TAGS


class TipoAcaoForm(forms.ModelForm):
    class Meta:
        model = TipoAcao
        fields = ['nome_acao', 'motivo_acao', 'mensagem_padrao_avaliacao', 'mensagem_padrao_conclusao']
        widgets = {
            'nome_acao':                    forms.TextInput(attrs={'class': 'form-control'}),
            'motivo_acao':                  forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'mensagem_padrao_avaliacao':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'mensagem_padrao_conclusao':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_nome_acao(self):
        return bleach.clean(self.cleaned_data['nome_acao'], tags=[], strip=True)

    def clean_motivo_acao(self):
        return bleach.clean(self.cleaned_data['motivo_acao'], tags=ALLOWED_TAGS, strip=True)

    def clean_mensagem_padrao_avaliacao(self):
        value = self.cleaned_data.get('mensagem_padrao_avaliacao') or ''
        return bleach.clean(value, tags=ALLOWED_TAGS, strip=True) or None

    def clean_mensagem_padrao_conclusao(self):
        value = self.cleaned_data.get('mensagem_padrao_conclusao') or ''
        return bleach.clean(value, tags=ALLOWED_TAGS, strip=True) or None


class AcaoForm(forms.ModelForm):
    data_execucao = forms.DateField(
        label="Data de Execução",
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        initial=datetime.date.today,
    )

    class Meta:
        model = Acao
        fields = ['data_execucao', 'tipo_acao', 'avaliacao', 'conclusao']
        widgets = {
            'tipo_acao': forms.Select(attrs={'class': 'form-select'}),
            'avaliacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'conclusao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_data_execucao(self):
        data = self.cleaned_data.get('data_execucao')
        if data and data > datetime.date.today():
            raise forms.ValidationError("A data de execução não pode ser no futuro.")
        return data

    def clean_avaliacao(self):
        return bleach.clean(self.cleaned_data['avaliacao'], tags=ALLOWED_TAGS, strip=True)

    def clean_conclusao(self):
        return bleach.clean(self.cleaned_data['conclusao'], tags=ALLOWED_TAGS, strip=True)
