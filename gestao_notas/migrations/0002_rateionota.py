# Generated by Django 5.0.2 on 2024-04-11 01:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_notas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RateioNota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('centro_de_custo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rateios', to='gestao_notas.centrodecusto')),
                ('nota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rateios', to='gestao_notas.nota')),
            ],
        ),
    ]
