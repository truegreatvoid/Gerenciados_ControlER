from django.urls import path
from .views import (
    EmitenteListView,
    EmitenteCreateView,
    EmitenteUpdateView,
    EmitenteDeleteView
)
app_name = 'gestao_notas'
urlpatterns = [
    path('emitentes/', EmitenteListView.as_view(), name='emitente_list'),
    path('emitentes/new/', EmitenteCreateView.as_view(), name='emitente_create'),
    path('emitentes/<int:pk>/edit/', EmitenteUpdateView.as_view(), name='emitente_update'),
    path('emitentes/<int:pk>/delete/', EmitenteDeleteView.as_view(), name='emitente_delete'),
]
