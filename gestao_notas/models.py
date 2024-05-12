from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Nota(models.Model):
    status = models.BooleanField(default=True)
    numero = models.CharField(max_length=20)
    serie = models.CharField(max_length=20, blank=True, null=True)
    data_emissao = models.DateField(blank=True, null=True)
    data_criacao = models.DateField(auto_now_add=True)
    chave_acesso = models.CharField(max_length=44, blank=True, null=True, db_index=True)
    natureza_operacao = models.CharField(max_length=255, blank=True, null=True)
    destinatario = models.ForeignKey('Destinatario', on_delete=models.CASCADE, related_name='notas_recebidas', blank=True, null=True)
    cfop = models.CharField(max_length=4, blank=True, null=True)
    informacoes_adicionais = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['data_criacao']

    def clean(self):
        # Verifica se a nota já foi salva (ou seja, tem uma chave primária)
        if self.pk:
            total_ratios = sum(ratio.valor for ratio in self.ratios.all())
            if total_ratios != self.valor_total:
                raise ValidationError(f"A soma dos valores dos Ratios deve ser igual a {self.valor_total}, mas é {total_ratios}.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    

class Ratio(models.Model):
    valor = models.IntegerField()
    descricao = models.CharField(max_length=255)
    nota = models.ForeignKey(Nota, related_name='ratios', on_delete=models.CASCADE)

class Categoria(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nome}"

class Cliente(models.Model):
    cliente = models.CharField(max_length=255)

    def __str__(self):
        return self.cliente

class Destinatario(models.Model):
    cliente = models.ForeignKey('Cliente', related_name='destinatarios', on_delete=models.CASCADE)
    obra = models.CharField(max_length=255)
    competencia = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.cliente} - {self.obra} - {self.competencia}"



class Recebimento(models.Model):
    destinatario = models.ForeignKey('Destinatario', on_delete=models.CASCADE, related_name='recebimentos')
    data_vencimento = models.DateField()
    valor = models.DecimalField(max_digits=20, decimal_places=2)
    parcelas = models.IntegerField()
    banco = models.CharField(max_length=255)
    data_criacao = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['data_criacao']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.pk:  # Garante que isso só aconteça na criação
            valor_parcela = self.valor / self.parcelas
            for i in range(self.parcelas):
                RecebimentoPagt.objects.create(
                    recebimento=self,
                    valor=valor_parcela,
                    numero_parcela=i + 1,
                    pago=False
                )

class RecebimentoPagt(models.Model):
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE, related_name='pagamentos')
    valor = models.DecimalField(max_digits=20, decimal_places=2)
    numero_parcela = models.IntegerField()
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"Parcela {self.numero_parcela} de {self.recebimento.valor_total} - {'Pago' if self.pago else 'Pendente'}"
