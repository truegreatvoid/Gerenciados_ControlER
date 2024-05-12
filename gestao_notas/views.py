from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.forms import inlineformset_factory

from reportlab.pdfgen import canvas
import openpyxl

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
import logging
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.forms import ValidationError
from django.urls import reverse

class NotaDeleteView(LoginRequiredMixin, DeleteView):
    model = Nota
    template_name = 'notas/nota_confirm_delete.html'  # Nome do template para confirmação de deleção
    success_url = reverse_lazy('gestao_notas:nota_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

class NotaUpdateView(UpdateView):
    model = Nota
    form_class = NotaForm
    template_name = 'notas/nota_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ratios'] = RatioFormSet(self.request.POST, instance=self.object)
        else:
            context['ratios'] = RatioFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ratios = context['ratios']
        if ratios.is_valid():
            total_ratios = sum(form.cleaned_data['valor'] for form in ratios.forms if form.is_valid() and not form.cleaned_data.get('DELETE', False))
            if total_ratios != form.cleaned_data['valor_total']:
                form.add_error('valor_total', ValidationError("A soma dos valores dos rateios deve ser igual ao valor total inserido."))
                return self.render_to_response(self.get_context_data(form=form))
            self.object = form.save()
            ratios.instance = self.object
            ratios.save()
            return redirect('gestao_notas:nota_list')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

# class NotaUpdateView(LoginRequiredMixin, UpdateView):
#     model = Nota
#     form_class = NotaForm
#     template_name = 'notas/nota_edit.html'
#     context_object_name = 'nota'
#     success_url = reverse_lazy('gestao_notas:nota_list')

#     def get_context_data(self, **kwargs):
#         data = super(NotaUpdateView, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['ratios'] = RatioFormSet(self.request.POST, instance=self.object)
#         else:
#             data['ratios'] = RatioFormSet(instance=self.object)
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         ratios = context['ratios']
#         if ratios.is_valid():
#             self.object = form.save(commit=False)  # Salva a Nota temporariamente sem commit
#             total_ratios = sum(ratio.cleaned_data.get('valor', 0) for ratio in ratios.forms if not ratio.cleaned_data.get('DELETE', False))
#             if total_ratios != self.object.valor_total:
#                 form.add_error(None, 'A soma dos valores dos Ratios deve ser igual ao valor total da Nota.')
#                 return self.form_invalid(form)
#             self.object.save()  # Salva a Nota permanentemente
#             ratios.instance = self.object
#             ratios.save()  # Salva os Ratios
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#             return self.form_invalid(form)


class NotaListView(LoginRequiredMixin, ListView):
    model = Nota
    template_name = 'notas/nota_list.html'
    context_object_name = 'notas'
    paginate_by = 10

    def get_queryset(self):
        return Nota.objects.all().order_by('data_criacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Debug para ver o contexto
        print(context)  # Isso imprimirá o contexto no console onde o servidor está rodando
        return context


class NotaDetailView(LoginRequiredMixin, DetailView):
    model = Nota
    template_name = 'notas/nota_detail.html'
    context_object_name = 'nota'
    


class NotaCreateView(CreateView):
    model = Nota
    form_class = NotaForm
    template_name = 'notas/nota_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ratios'] = RatioFormSet(self.request.POST, instance=self.object if self.object else None)
        else:
            context['ratios'] = RatioFormSet(instance=self.object if self.object else None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ratios = context['ratios']
        if ratios.is_valid():
            total_ratios = 0
            for ratio_form in ratios.forms:
                if not ratio_form.cleaned_data.get('DELETE', False):
                    total_ratios += ratio_form.cleaned_data.get('valor', 0)

            if total_ratios != form.cleaned_data.get('valor_total'):
                form.add_error('valor_total', ValidationError("A soma dos valores dos rateios deve ser igual ao valor total."))
                return self.render_to_response(self.get_context_data(form=form))
            self.object = form.save(commit=False)
            self.object.save()
            ratios.instance = self.object
            ratios.save()
            return redirect('gestao_notas:nota_list')   # Assegure-se de que este método está definido
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


# class NotaCreateView(LoginRequiredMixin, CreateView):
#     model = Nota
#     form_class = NotaForm
#     template_name = 'notas/nota_create.html'

#     def get_context_data(self, **kwargs):
#         data = super(NotaCreateView, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['ratios'] = RatioFormSet(self.request.POST)
#         else:
#             data['ratios'] = RatioFormSet()
#         return data

#     def form_valid(self, form):
#         context = self.get_context_data()
#         ratios = context['ratios']
#         if ratios.is_valid():
#             self.object = form.save(commit=False)  # Salva a Nota temporariamente sem commit
#             total_ratios = sum(ratio.cleaned_data.get('valor', 0) for ratio in ratios.forms if not ratio.cleaned_data.get('DELETE', False))
#             if total_ratios != self.object.valor_total:
#                 form.add_error(None, 'A soma dos valores dos Ratios deve ser igual ao valor total da Nota.')
#                 return self.form_invalid(form)
#             self.object.save()  # Salva a Nota permanentemente
#             ratios.instance = self.object
#             ratios.save()  # Salva os Ratios
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#             return self.form_invalid(form)

#     def get_success_url(self):
#         return reverse_lazy('gestao_notas:nota_list')

# RatioInlineFormSet = inlineformset_factory(
#     Nota, Ratio, form=RatioForm, extra=1, can_delete=True)


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




# Views para Categoria

class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'categorias/categoria_list.html'


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categorias/categoria_form.html'
    success_url = reverse_lazy('gestao_notas:categoria_list')


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categorias/categoria_form.html'
    success_url = reverse_lazy('gestao_notas:categoria_list')


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'categorias/categoria_confirm_delete.html'
    success_url = reverse_lazy('gestao_notas:categoria_list')


class CategoriaDetailView(LoginRequiredMixin, DetailView):
    model = Categoria
    template_name = 'categorias/categoria_detail.html'

# # Views para Destinatario

class DestinatarioListView(LoginRequiredMixin, ListView):
    model = Destinatario
    template_name = 'destinatarios/destinatario_list.html'


class DestinatarioCreateView(LoginRequiredMixin, CreateView):
    model = Destinatario
    form_class = DestinatarioForm
    template_name = 'destinatarios/destinatario_form.html'
    success_url = reverse_lazy('gestao_notas:destinatario_list')


class DestinatarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Destinatario
    form_class = DestinatarioForm
    template_name = 'destinatarios/destinatario_form.html'
    success_url = reverse_lazy('gestao_notas:destinatario_list')


class DestinatarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Destinatario
    template_name = 'destinatarios/destinatario_confirm_delete.html'
    success_url = reverse_lazy('gestao_notas:destinatario_list')


class DestinatarioDetailView(LoginRequiredMixin, DetailView):
    model = Destinatario
    template_name = 'destinatarios/destinatario_detail.html'


# Views para Clientes

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/clientes_list.html'


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/clientes_form.html'
    success_url = reverse_lazy('gestao_notas:cliente_list')


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/clientes_form.html'
    success_url = reverse_lazy('gestao_notas:cliente_list')


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/clientes_confirm_delete.html'
    success_url = reverse_lazy('gestao_notas:cliente_list')


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/clientes_detail.html'



# Views para Recebimento

class RecebimentoListView(LoginRequiredMixin, ListView):
    model = Recebimento
    template_name = 'recebimento/recebimento_list.html'

    def get_queryset(self):
        return Recebimento.objects.all().order_by('data_criacao')


class RecebimentoCreateView(LoginRequiredMixin, CreateView):
    model = Recebimento
    form_class = RecebimentoForm
    template_name = 'recebimento/recebimento_form.html'
    success_url = reverse_lazy('gestao_notas:recebimento_list')


class RecebimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Recebimento
    form_class = RecebimentoForm
    template_name = 'recebimento/recebimento_form.html'
    success_url = reverse_lazy('gestao_notas:recebimento_list')

    def get_context_data(self, **kwargs):
        data = super(RecebimentoUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['pagamentos'] = RecebimentoPagtFormSet(self.request.POST, instance=self.object)
        else:
            data['pagamentos'] = RecebimentoPagtFormSet(instance=self.object)
        return data



    def form_valid(self, form):
        context = self.get_context_data()
        pagamentos = context['pagamentos']
        if pagamentos.is_valid():
            self.object = form.save()
            pagamentos.instance = self.object
            pagamentos.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class RecebimentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Recebimento
    template_name = 'recebimento/recebimento_confirm_delete.html'
    success_url = reverse_lazy('gestao_notas:recebimento_list')


class RecebimentoDetailView(LoginRequiredMixin, DetailView):
    model = Recebimento
    template_name = 'recebimento/recebimento_detail.html'



logger = logging.getLogger(__name__)


#Login
class CustomLoginView(LoginView):
    template_name = 'login/login.html'
    form_class = LoginForm
    next_page = reverse_lazy('gestao_notas:nota_list')

    def dispatch(self, request, *args, **kwargs):
        # Se o usuário já estiver autenticado e tentar acessar a tela de login, redirecione para outra página (ou trate de forma diferente)
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.next_page



class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('gestao_notas:login')



