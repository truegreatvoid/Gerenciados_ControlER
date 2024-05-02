from django.contrib import admin
from .models import *

class RatioInline(admin.TabularInline):
    model = Ratio
    extra = 1

class NotaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'serie', 'data_emissao', 'status', 'list_ratios')
    search_fields = ('numero', 'serie', 'chave_acesso')
    list_filter = ('status', 'data_emissao')
    date_hierarchy = 'data_emissao'
    inlines = [RatioInline]

    def list_ratios(self, obj):
        ratios = obj.ratios.all()
        if ratios:
            return ', '.join(f'{ratio.valor} ({ratio.descricao})' for ratio in ratios)
        return "Nenhum ratio"
    list_ratios.short_description = 'Ratios'  # Define o cabeçalho da coluna no admin



admin.site.register(Nota, NotaAdmin)
admin.site.register(Categoria)
admin.site.register(Ratio)  # Ratio ainda pode ser registrado como um modelo separado, se necessário
admin.site.register(Destinatario)
