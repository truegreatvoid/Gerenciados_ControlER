from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('gestao-notas/', include(('gestao_notas.urls', 'gestao_notas')), name='gestao_notas'),
    path('ceo-controler/', admin.site.urls),
]