from django.contrib import admin
from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

app_name = 'gestao_notas'

urlpatterns = [
    path('notas/', NotaListView.as_view(), name='nota_list'),
    path('notas/<int:pk>/', NotaDetailView.as_view(), name='nota_detail'),
    path('notas/nova/', NotaCreateView.as_view(), name='nota_create'),  # URL para criar uma nova Nota
    path('exportar-xlsx/', exportar_xlsx, name='exportar_xlsx'),
    path('exportar-pdf/', exportar_pdf, name='exportar_pdf'),
    path('notas/editar/<int:pk>/', NotaUpdateView.as_view(), name='nota_edit'),
    path('notas/deletar/<int:pk>/', NotaDeleteView.as_view(), name='nota_delete'),

    path('add-nota/', NotaCreateView.as_view(), name='add-nota'),

    # URLs para Categoria
    path('categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/create/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/update/<int:pk>/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/delete/<int:pk>/', CategoriaDeleteView.as_view(), name='categoria_delete'),
    path('categorias/<int:pk>/', CategoriaDetailView.as_view(), name='categoria_detail'),

    # # URLs para Destinatario
    path('destinatarios/', DestinatarioListView.as_view(), name='destinatario_list'),
    path('destinatarios/create/', DestinatarioCreateView.as_view(), name='destinatario_create'),
    path('destinatarios/update/<int:pk>/', DestinatarioUpdateView.as_view(), name='destinatario_update'),
    path('destinatarios/delete/<int:pk>/', DestinatarioDeleteView.as_view(), name='destinatario_delete'),
    path('destinatarios/<int:pk>/', DestinatarioDetailView.as_view(), name='destinatario_detail'),

    # # URLs para Clientes
    path('cliente/', ClienteListView.as_view(), name='cliente_list'),
    path('cliente/create/', ClienteCreateView.as_view(), name='cliente_create'),
    path('cliente/update/<int:pk>/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('cliente/delete/<int:pk>/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('cliente/<int:pk>/', ClienteDetailView.as_view(), name='cliente_detail'),

    # # URLs para Recebimento
    path('recebimentos/', RecebimentoListView.as_view(), name='recebimento_list'),
    path('recebimentos/create/', RecebimentoCreateView.as_view(), name='recebimento_create'),
    path('recebimentos/update/<int:pk>/', RecebimentoUpdateView.as_view(), name='recebimento_update'),
    path('recebimentos/delete/<int:pk>/', RecebimentoDeleteView.as_view(), name='recebimento_delete'),
    path('recebimentos/<int:pk>/', RecebimentoDetailView.as_view(), name='recebimento_detail'),

    #login/logout
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
