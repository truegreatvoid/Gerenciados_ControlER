# No seu app Django, crie um arquivo `templatetags/my_tags.py`
from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='days_since')
def days_since(value):
    """Calcula a diferença em dias entre a data fornecida e hoje."""
    if not value:
        return 0
    delta = datetime.now().date() - value.date()
    return delta.days

@register.filter(name='ponto_por_virgula')
def ponto_por_virgula(value):
    return str(value).replace(',', '.')