from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include(('gestao_notas.urls', 'gestao_notas'), namespace='gestao_notas')),
    path('ceo-controler/', admin.site.urls),
]