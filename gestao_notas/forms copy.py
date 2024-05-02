from django import forms
from django.forms import inlineformset_factory, ModelForm
from .models import Nota, Ratio
from django.forms import ModelForm

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = '__all__'

# Formset para os objetos Ratio relacionados à Nota
RatioFormSet = inlineformset_factory(Nota, Ratio, fields=('valor', 'descricao'), extra=1)

class RatioForm(ModelForm):
    class Meta:
        model = Ratio
        fields = ['valor', 'descricao']