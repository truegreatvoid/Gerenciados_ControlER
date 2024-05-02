from django import forms
from .models import Nota, Categoria

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['numero', 'data_emissao', 'categoria', 'emitente', 'destinatario', 'status', 'categoria']  # Removi 'valor_total'
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

