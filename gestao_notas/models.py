from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, F


class Emitente(models.Model):
    nome_razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, validators=[RegexValidator(r'\d{14}', 'CNPJ deve ter 14 dígitos.')], db_index=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField()

    def __str__(self):
        return self.nome_razao_social

class Destinatario(models.Model):
    nome_razao_social = models.CharField(max_length=255)
    cpf_cnpj = models.CharField(max_length=18, db_index=True)
    endereco = models.TextField()

    def __str__(self):
        return self.nome_razao_social

class Produto(models.Model):
    descricao = models.CharField(max_length=255)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    unidade = models.CharField(max_length=20)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    codigo = models.CharField(max_length=100)
    ncm_sh = models.CharField(max_length=10)

    def __str__(self):
        return self.descricao

class Nota(models.Model):
    numero = models.CharField(max_length=20)
    serie = models.CharField(max_length=20, blank=True, null=True)
    data_emissao = models.DateField()
    data_operacao = models.DateField()
    chave_acesso = models.CharField(max_length=44, blank=True, null=True, db_index=True)
    natureza_operacao = models.CharField(max_length=255)
    emitente = models.ForeignKey(Emitente, on_delete=models.CASCADE, related_name='notas_emitidas')
    destinatario = models.ForeignKey(Destinatario, on_delete=models.CASCADE, related_name='notas_recebidas')
    produtos = models.ManyToManyField(Produto, through='ItemNota')
    cfop = models.CharField(max_length=4)
    informacoes_adicionais = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)  # Classifica a nota
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def clean(self):
        # Validações customizadas para garantir a integridade dos dados
        super().clean()  # Chama a limpeza padrão primeiro para completar a validação do modelo
        if self.chave_acesso and Nota.objects.filter(chave_acesso=self.chave_acesso).exclude(id=self.id).exists():
            raise ValidationError("Chave de acesso já cadastrada.")

    @property
    def valor_total(self):
        # Calcula a soma dos valores totais dos itens relacionados
        # Aqui utilizamos 'F' para multiplicar quantidade por valor_unitario diretamente no banco de dados
        total = self.itemnota_set.annotate(
            item_total=F('quantidade') * F('valor_unitario')
        ).aggregate(
            total=Sum('item_total')
        )['total']
        return total or 0

    def __str__(self):
        return f'Nota {self.numero} - {self.emitente.nome_razao_social}'
        
class RateioNota(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE, related_name='rateios')
    centro_de_custo = models.ForeignKey('CentroDeCusto', on_delete=models.CASCADE, related_name='rateios')
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Adicionando o campo valor

    def __str__(self):
        return f'{self.centro_de_custo.nome}: {self.valor}'


class ItemNota(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('nota', 'produto')

    @property
    def valor_total(self):
        if self.quantidade is not None and self.valor_unitario is not None:
            return self.quantidade * self.valor_unitario
        return 0

    def __str__(self):
        return f'{self.quantidade} x {self.produto.descricao} em Nota {self.nota.numero}'

class CentroDeCusto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)


    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)  # Por exemplo: Despesa, Entrada, Saída

    def __str__(self):
        return self.nome

# Adicionando uma relação com Categoria no modelo Nota
Nota.categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
