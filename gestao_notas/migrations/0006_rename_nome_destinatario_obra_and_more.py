# Generated by Django 5.0.2 on 2024-05-12 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_notas', '0005_cliente_alter_recebimento_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='destinatario',
            old_name='nome',
            new_name='obra',
        ),
        migrations.RemoveField(
            model_name='destinatario',
            name='documento',
        ),
        migrations.AddField(
            model_name='destinatario',
            name='competencia',
            field=models.DateField(blank=True, null=True),
        ),
    ]
