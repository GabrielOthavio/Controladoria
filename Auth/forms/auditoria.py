import bleach
from django import forms
from ..models import Auditoria, MatrizAuditoria, EntidadeAuditoria, Etapa, Achado
from .utils import ALLOWED_TAGS


class AuditoriaForm(forms.ModelForm):
    class Meta:
        model = Auditoria
        fields = [
            'nome_auditoria', 'status', 'matriz',
            'orgao', 'responsavel_orgao',
            'data_inicio', 'data_conclusao',
            'usuarios_envolvidos', 'informacoes_campos_texto',
        ]
        widgets = {
            'nome_auditoria':           forms.TextInput(attrs={'class': 'form-control'}),
            'status':                   forms.Select(attrs={'class': 'form-select'}),
            'matriz':                   forms.Select(attrs={'class': 'form-select'}),
            'orgao':                    forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_orgao':        forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio':              forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'data_conclusao':           forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'usuarios_envolvidos':      forms.CheckboxSelectMultiple(),
            'informacoes_campos_texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_nome_auditoria(self):
        return bleach.clean(self.cleaned_data['nome_auditoria'], tags=[], strip=True)

    def clean_orgao(self):
        value = self.cleaned_data.get('orgao') or ''
        return bleach.clean(value, tags=[], strip=True) or None

    def clean_responsavel_orgao(self):
        value = self.cleaned_data.get('responsavel_orgao') or ''
        return bleach.clean(value, tags=[], strip=True) or None

    def clean_informacoes_campos_texto(self):
        value = self.cleaned_data.get('informacoes_campos_texto', '')
        return bleach.clean(value, tags=ALLOWED_TAGS, strip=True)


class EtapaForm(forms.ModelForm):
    class Meta:
        model = Etapa
        fields = ['orientacao', 'documentos', 'usuario', 'atividade', 'prazo', 'situacao', 'metodo']
        widgets = {
            'orientacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documentos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'usuario':    forms.Select(attrs={'class': 'form-select'}),
            'atividade':  forms.TextInput(attrs={'class': 'form-control'}),
            'prazo':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'situacao':   forms.Select(attrs={'class': 'form-select'}),
            'metodo':     forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_orientacao(self):
        return bleach.clean(self.cleaned_data['orientacao'], tags=ALLOWED_TAGS, strip=True)

    def clean_documentos(self):
        value = self.cleaned_data.get('documentos', '')
        return bleach.clean(value, tags=ALLOWED_TAGS, strip=True)

    def clean_atividade(self):
        return bleach.clean(self.cleaned_data['atividade'], tags=[], strip=True)

    def clean_metodo(self):
        value = self.cleaned_data.get('metodo', '')
        return bleach.clean(value, tags=[], strip=True)


class AchadoForm(forms.ModelForm):
    class Meta:
        model = Achado
        fields = ['descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva o achado…'}),
        }

    def clean_descricao(self):
        return bleach.clean(self.cleaned_data['descricao'], tags=ALLOWED_TAGS, strip=True)


class MatrizAuditoriaForm(forms.ModelForm):
    class Meta:
        model = MatrizAuditoria
        fields = [
            'descricao', 'objetivo',
            'base_legal', 'riscos',
            'criterios_indicadores', 'procedimentos',
            'conclusoes_esperadas', 'entidade',
            'observacoes',
        ]
        widgets = {
            'descricao':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição'}),
            'objetivo':              forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Objetivo'}),
            'base_legal':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Base Legal'}),
            'riscos':                forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Riscos'}),
            'criterios_indicadores': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Criterios Indicadores'}),
            'procedimentos':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Procedimentos Auditoria'}),
            'conclusoes_esperadas':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Conclusões Esperadas'}),
            'entidade':              forms.Select(attrs={'class': 'form-select'}),
            'observacoes':           forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações'}),
        }

    def clean_descricao(self):
        return bleach.clean(self.cleaned_data['descricao'], tags=[], strip=True)

    def clean_objetivo(self):
        return bleach.clean(self.cleaned_data['objetivo'], tags=ALLOWED_TAGS, strip=True)

    def clean_base_legal(self):
        return bleach.clean(self.cleaned_data['base_legal'], tags=[], strip=True)

    def clean_riscos(self):
        return bleach.clean(self.cleaned_data['riscos'], tags=[], strip=True)

    def clean_criterios_indicadores(self):
        return bleach.clean(self.cleaned_data['criterios_indicadores'], tags=[], strip=True)

    def clean_procedimentos(self):
        return bleach.clean(self.cleaned_data['procedimentos'], tags=[], strip=True)

    def clean_conclusoes_esperadas(self):
        return bleach.clean(self.cleaned_data['conclusoes_esperadas'], tags=[], strip=True)

    def clean_observacoes(self):
        return bleach.clean(self.cleaned_data['observacoes'], tags=ALLOWED_TAGS, strip=True)


class EntidadeAuditoriaForm(forms.ModelForm):
    class Meta:
        model = EntidadeAuditoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nome(self):
        return bleach.clean(self.cleaned_data['nome'], tags=[], strip=True)


class GerarRelatorioForm(forms.Form):
    TIPO_RELATORIO_CHOICES = [
        ('AUDITORIA', 'Auditorias'),
        ('ACAO', 'Ações'),
        ('INDICE', 'Índices'),
    ]
    nome_relatorio = forms.CharField(
        label="Nome do Relatório",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    tipo_relatorio = forms.ChoiceField(
        label="Tipo de Relatório",
        choices=TIPO_RELATORIO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    data_inicio = forms.DateField(
        label="Data de Início",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
    )

    def clean_nome_relatorio(self):
        return bleach.clean(self.cleaned_data['nome_relatorio'], tags=[], strip=True)

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        if data_inicio and data_fim and data_fim < data_inicio:
            raise forms.ValidationError("A data final não pode ser anterior à data inicial.")
        return cleaned_data
