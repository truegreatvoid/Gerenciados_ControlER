# Generated by Django 5.0.2 on 2024-04-14 15:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_notas', '0003_rename_valor_rateionota_ratio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destinatario',
            name='cpf_cnpj',
            field=models.CharField(db_index=True, max_length=18),
        ),
        migrations.AlterField(
            model_name='emitente',
            name='cnpj',
            field=models.CharField(db_index=True, max_length=18, validators=[django.core.validators.RegexValidator('\\d{14}', 'CNPJ deve ter 14 dígitos.')]),
        ),
        migrations.AlterField(
            model_name='nota',
            name='chave_acesso',
            field=models.CharField(blank=True, db_index=True, max_length=44, null=True),
        ),
    ]
