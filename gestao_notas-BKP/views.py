from django.views.generic.list import ListView
from .models import Nota

from reportlab.pdfgen import canvas
import openpyxl
from django.http import HttpResponse


from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Sum, F

from .forms import NotaForm


class NotaCreateView(CreateView):
    model = Nota
    form_class = NotaForm
    template_name = 'nota_form.html'
    success_url = reverse_lazy('gestao_notas:nota_list')

class NotaUpdateView(UpdateView):
    model = Nota
    form_class = NotaForm
    template_name = 'nota_form.html'
    success_url = reverse_lazy('gestao_notas:nota_list')


class NotaListView(ListView):
    model = Nota
    template_name = 'consultar_notas.html'
    context_object_name = 'notas_detalhes'

    def get_queryset(self):
        # Preloading related data and calculating sum of 'valor' in 'rateios'
        return Nota.objects.select_related('emitente', 'categoria').prefetch_related('rateios', 'rateios__centro_de_custo').annotate(
            total_rateio=Sum(F('rateios__valor'))
        )

    def get_context_data(self, **kwargs):
        context = super(NotaListView, self).get_context_data(**kwargs)
        notas_detalhes = []
        

        for nota in context['notas_detalhes']:
            total_rateio = nota.total_rateio if hasattr(nota, 'total_rateio') else 0
            rateio_correto = (total_rateio == nota.valor_total)
            cfop = cfop
            notas_detalhes.append({
                'nota': nota,
                'cfop':cfop,
                'total_rateio': total_rateio,
                'rateio_correto': rateio_correto
            })

        context['notas_detalhes'] = notas_detalhes
        return context



def add_nota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            created_nota = form.save(commit=False)
            formset = RatioFormSet(request.POST, instance=created_nota)
            if formset.is_valid():
                created_nota.save()  # Salva Nota primeiro para garantir que tenha um ID
                formset.save()       # Salva os Ratios relacionados
                # Após salvar tudo, verifica a soma dos Ratios
                if not validate_ratios(created_nota):
                    form.add_error(None, 'A soma dos valores dos Ratios não corresponde ao valor total da Nota.')
                    created_nota.delete()  # Opção para deletar a nota se a validação falhar
                    return render(request, 'add_nota.html', {'form': form, 'formset': formset})
                return redirect('some_view')
    else:
        form = NotaForm()
        formset = RatioFormSet()

    return render(request, 'add_nota.html', {'form': form, 'formset': formset})

def validate_ratios(nota):
    total_ratios = sum(ratio.valor for ratio in nota.ratios.all())
    return total_ratios == nota.valor_total

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



