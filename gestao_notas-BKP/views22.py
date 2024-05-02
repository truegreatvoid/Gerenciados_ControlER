from django.views.generic.list import ListView
from .models import Nota

from reportlab.pdfgen import canvas
import openpyxl
from django.http import HttpResponse

class NotaListView(ListView):
    model = Nota
    template_name = 'consultar_notas.html'
    context_object_name = 'notas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o valor total e verificações de rateio ao contexto
        context['notas_detalhes'] = [
            {
                'nota': nota,
                'total_rateio': sum(rateio.valor for rateio in nota.rateios.all()),
                'valor_total': nota.valor_total,  # Uso da propriedade aqui
                'rateio_correto': sum(rateio.valor for rateio in nota.rateios.all()) == nota.valor_total
            }
            for nota in context['notas']
        ]
        return context

def exportar_xlsx(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=notas.xlsx'
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notas"

    # Cabeçalhos
    columns = ["Nota Número", "Data Emissão", "Valor Total da Nota", "Total Rateio", "Rateio Correto"]
    ws.append(columns)

    # Dados
    notas = Nota.objects.all()
    for nota in notas:
        total_rateio = sum(rateio.valor for rateio in nota.rateios.all())
        rateio_correto = total_rateio == nota.valor_total
        ws.append([
            nota.numero,
            nota.data_emissao,
            nota.valor_total,
            total_rateio,
            "Sim" if rateio_correto else "Não",
        ])

    wb.save(response)
    return response

def exportar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="notas.pdf"'

    p = canvas.Canvas(response)
    y = 800  # Posição inicial no PDF

    # Cabeçalhos
    p.drawString(50, y, "Nota Número")
    p.drawString(150, y, "Data Emissão")
    p.drawString(250, y, "Valor Total")
    p.drawString(350, y, "Total Rateio")
    p.drawString(450, y, "Rateio Correto")

    notas = Nota.objects.all()
    for nota in notas:
        y -= 20
        total_rateio = sum(rateio.valor for rateio in nota.rateios.all())
        rateio_correto = total_rateio == nota.valor_total
        p.drawString(50, y, str(nota.numero))
        p.drawString(150, y, str(nota.data_emissao))
        p.drawString(250, y, str(nota.valor_total))
        p.drawString(350, y, str(total_rateio))
        p.drawString(450, y, "Sim" if rateio_correto else "Não")

    p.showPage()
    p.save()
    return response