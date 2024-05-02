from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Nota, Ratio
from .forms import NotaForm, RatioForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.forms import inlineformset_factory

from reportlab.pdfgen import canvas
import openpyxl

class NotaDeleteView(DeleteView):
    model = Nota
    template_name = 'notas/nota_confirm_delete.html'  # Nome do template para confirmação de deleção
    success_url = reverse_lazy('gestao_notas:nota_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

class NotaUpdateView(UpdateView):
    model = Nota
    form_class = NotaForm
    template_name = 'notas/nota_edit.html'  # Nome do template que você precisa criar
    context_object_name = 'nota'
    success_url = reverse_lazy('gestao_notas:nota_list')  # Redireciona após a edição bem-sucedida

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

class NotaListView(ListView):
    model = Nota
    template_name = 'notas/nota_list.html'
    context_object_name = 'notas'

class NotaDetailView(DetailView):
    model = Nota
    template_name = 'notas/nota_detail.html'
    context_object_name = 'nota'


class NotaCreateView(CreateView):
    model = Nota
    form_class = NotaForm
    template_name = 'notas/nota_create.html'

    def get_context_data(self, **kwargs):
        data = super(NotaCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['ratios'] = RatioInlineFormSet(self.request.POST)
        else:
            data['ratios'] = RatioInlineFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ratios = context['ratios']
        if ratios.is_valid():
            self.object = form.save()
            ratios.instance = self.object
            ratios.save()
            if self.object.valor_total != sum(ratio.valor for ratio in self.object.ratios.all()):
                form.add_error(None, 'A soma dos valores dos Ratios deve ser igual ao valor total da Nota.')
                return self.form_invalid(form)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('gestao_notas:nota_list')


RatioInlineFormSet = inlineformset_factory(
    Nota, Ratio, form=RatioForm, extra=1, can_delete=True)


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
        
        
        ws.append([
            nota.numero,
            nota.data_emissao,
            nota.valor_total,

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

        p.drawString(50, y, str(nota.numero))
        p.drawString(150, y, str(nota.data_emissao))
        p.drawString(250, y, str(nota.valor_total))


    p.showPage()
    p.save()
    return response



