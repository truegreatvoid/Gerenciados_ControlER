from django.contrib import admin
from .models import *

# Classe Inline para editar Ratios diretamente na página de edição de Nota
class RatioInline(admin.TabularInline):
    model = Ratio
    extra = 1  # Define quantos campos para novos objetos Ratio serão mostrados por padrão

# Configurações do Admin para o modelo Nota
class NotaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'serie', 'data_emissao', 'status', 'list_ratios')
    search_fields = ('numero', 'serie', 'chave_acesso')
    list_filter = ('status', 'data_emissao')
    date_hierarchy = 'data_emissao'  # Adiciona um navegador por datas para o campo data_emissao
    inlines = [RatioInline]

    def list_ratios(self, obj):
        ratios = obj.ratios.all()
        return ', '.join(f'{ratio.valor} ({ratio.descricao})' for ratio in ratios) if ratios else "Nenhum ratio"
    list_ratios.short_description = 'Ratios'



# Inline Admin para RecebimentoPagt
class RecebimentoPagtInline(admin.TabularInline):
    model = RecebimentoPagt
    extra = 0
    fields = ['numero_parcela', 'valor', 'pago']
    readonly_fields = ['numero_parcela', 'valor']
    can_delete = False

# Administração simplificada para Destinatario
class DestinatarioAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'obra', 'competencia']
    search_fields = ['cliente', 'obra', 'competencia']

# Configurações do Admin para o modelo Recebimento
class RecebimentoAdmin(admin.ModelAdmin):
    list_display = ['destinatario', 'valor', 'data_vencimento', 'parcelas', 'banco']
    list_filter = ['banco', 'data_vencimento']
    search_fields = ['destinatario__nome', 'banco']
    inlines = [RecebimentoPagtInline]


# Registro de modelos no admin
admin.site.register(Recebimento, RecebimentoAdmin)
admin.site.register(Destinatario, DestinatarioAdmin)
admin.site.register(Nota, NotaAdmin)
admin.site.register(Categoria)
admin.site.register(Ratio)  # Se desejar administrar Ratios separadamente
