from django import forms
from django.forms import inlineformset_factory, ModelForm
from .models import *
from django.contrib.auth.forms import AuthenticationForm

from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuário'}), label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'}), label='')



class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = '__all__'  # ou especifique campos específicos
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'data_emissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'chave_acesso': forms.TextInput(attrs={'class': 'form-control'}),
            'natureza_operacao': forms.TextInput(attrs={'class': 'form-control'}),
            'destinatario': forms.Select(attrs={'class': 'form-control'}),
            'cfop': forms.TextInput(attrs={'class': 'form-control'}),
            'informacoes_adicionais': forms.Textarea(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    # def __init__(self, *args, **kwargs):
    #     super(NotaForm, self).__init__(*args, **kwargs)
    #     for field_name, field in self.fields.items():
    #         field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        valor_total = cleaned_data.get('valor_total')
        ratios = self.cleaned_data.get('ratios')
        
        if ratios and sum(ratio.cleaned_data.get('valor', 0) for ratio in ratios) != valor_total:
            raise ValidationError("A soma dos valores dos ratios deve igualar o valor total da nota.")

class RatioForm(forms.ModelForm):
    class Meta:
        model = Ratio
        fields = '__all__'
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
        }
RatioFormSet = forms.inlineformset_factory(Nota, Ratio, form=RatioForm, fields=('valor', 'descricao'), extra=0, can_delete=True)
# RatioFormSet = inlineformset_factory(Nota, Ratio, fields=('valor', 'descricao'), extra=0, can_delete=True)

# class NotaForm(forms.ModelForm):
#     class Meta:
#         model = Nota
#         fields = ['numero', 'serie', 'data_emissao', 'chave_acesso', 'natureza_operacao', 'destinatario', 'cfop', 'informacoes_adicionais', 'categoria', 'valor_total']

#     def __init__(self, *args, **kwargs):
#         super(NotaForm, self).__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'

# class RatioForm(ModelForm):
#     class Meta:
#         model = Ratio
#         fields = ['valor', 'descricao']

#     def __init__(self, *args, **kwargs):
#         super(RatioForm, self).__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'

# Formset para os objetos Ratio relacionados à Nota
# RatioFormSet = inlineformset_factory(
#     Nota, Ratio, form=RatioForm, fields=('valor', 'descricao'), extra=1, can_delete=True
# )
# RatioFormSet = inlineformset_factory(
#     Nota, Ratio, form=RatioForm, fields=('valor', 'descricao'), extra=1, can_delete=True
# )

# RatioFormSet = inlineformset_factory(Nota, Ratio, form=RatioForm, extra=1, can_delete=True)

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

    def __init__(self, *args, **kwargs):
        super(CategoriaForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cliente']

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class DestinatarioForm(forms.ModelForm):
    class Meta:
        model = Destinatario
        fields = ['cliente', 'obra', 'competencia']

    def __init__(self, *args, **kwargs):
        super(DestinatarioForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['competencia'].widget = forms.DateInput(
            attrs={
                'class': 'form-control',  # Mantenha a consistência do estilo
                'type': 'date'            # Tipo de entrada como data
            },
            format='%Y-%m-%d'             # Formato de data que o HTML5 date input espera
        )

class RecebimentoForm(forms.ModelForm):
    class Meta:
        model = Recebimento
        fields = ['destinatario', 'data_vencimento', 'valor', 'parcelas', 'banco']

    def __init__(self, *args, **kwargs):
        super(RecebimentoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return valor

    def clean_parcelas(self):
        parcelas = self.cleaned_data.get('parcelas')
        if parcelas <= 0:
            raise forms.ValidationError("O número de parcelas deve ser maior que zero.")
        return parcelas

    def save(self, commit=True):
        recebimento = super().save(commit=False)  # Salva o objeto Recebimento sem cometer no DB
        if commit:
            recebimento.save()  # Comete o objeto Recebimento no DB
            self.save_recebimento_pagt(recebimento)  # Cria e salva os objetos RecebimentoPagt
        return recebimento

    def save_recebimento_pagt(self, recebimento):
        valor_parcela = recebimento.valor / recebimento.parcelas
        for i in range(recebimento.parcelas):
            RecebimentoPagt.objects.create(
                recebimento=recebimento,
                valor=valor_parcela,
                numero_parcela=i + 1,
                pago=False
            )


class RecebimentoPagtForm(ModelForm):
    class Meta:
        model = RecebimentoPagt
        fields = ['recebimento', 'valor', 'numero_parcela', 'pago']

    def __init__(self, *args, **kwargs):
        super(RecebimentoPagtForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

RecebimentoPagtFormSet = inlineformset_factory(
    Recebimento,
    RecebimentoPagt,
    form=RecebimentoPagtForm,
    fields=['valor', 'numero_parcela', 'pago'],
    extra=1,  # Permite adicionar pelo menos um novo formulário de pagamento ao formset
    can_delete=True  # Permite deletar pagamentos existentes
)


