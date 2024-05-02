from django.urls import path
from .views import NotaListView, exportar_xlsx, exportar_pdf

app_name = 'gestao_notas'

urlpatterns = [
    path('', NotaListView.as_view(), name='consultar_notas'),
    path('notas/', NotaListView.as_view(), name='lista_notas'),
    path('exportar-xlsx/', exportar_xlsx, name='exportar_xlsx'),
    path('exportar-pdf/', exportar_pdf, name='exportar_pdf'),
]