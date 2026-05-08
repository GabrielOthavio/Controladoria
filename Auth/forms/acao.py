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
            'nome_acao':                    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fiscalização, Inspeção, Auditoria Interna…'}),
            'motivo_acao':                  forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o motivo que justifica este tipo de ação…'}),
            'mensagem_padrao_avaliacao':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Texto que será sugerido automaticamente no campo Avaliação ao usar este tipo…'}),
            'mensagem_padrao_conclusao':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Texto que será sugerido automaticamente no campo Conclusão ao usar este tipo…'}),
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
        help_text="Informe a data em que a ação foi realizada. Datas futuras não são permitidas.",
    )

    class Meta:
        model = Acao
        fields = ['data_execucao', 'tipo_acao', 'unidade', 'status', 'is_paint', 'avaliacao', 'conclusao']
        widgets = {
            'tipo_acao': forms.Select(attrs={'class': 'form-select'}),
            'unidade':   forms.Select(attrs={'class': 'form-select'}),
            'status':    forms.Select(attrs={'class': 'form-select'}),
            'is_paint':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'avaliacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva a avaliação da ação realizada…'}),
            'conclusao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Registre a conclusão ou resultado obtido…'}),
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
