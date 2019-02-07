import os
from binascii import hexlify
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView

from .models import *
from .forms import *

# Create your views here.
def index(request):
    return redirect('/printers/')


class PrinterList(ListView):
    model = Printer

    def get_queryset(self):
        return Printer.objects.filter(user=self.request.user)

class PrinterDetail(DetailView):
    form_class = PrinterForm
    model = Printer
    template_name = 'app/printer_wizard.html'

    def get_object(self):
        if self.kwargs['pk'] == 'new':
            return None
        else:
            return get_object_or_404(Printer, pk=self.kwargs['pk'], user=self.request.user)

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object())
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES or None, instance=self.get_object())
        if form.is_valid():
            if kwargs['pk'] == 'new':
                printer = form.save(commit=False)
                printer.user = request.user
                printer.auth_token = hexlify(os.urandom(10)).decode()
                printer.save()
                return redirect('/printers/{}/#step-2'.format(printer.id))
            else:
                form.save()
                return render(request, self.template_name, {'form': form})

        return render(request, self.template_name, {'form': form})

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return redirect('/printers/')

@login_required
def cancel_printer(request, id):
    get_object_or_404(Printer, id=id)
    instance.delete()
    return redirect('/printers/')


@login_required
def delete_printer(request, id):
    instance = get_object_or_404(Printer, id=id)
    instance.delete()
    return redirect('/printers/')

def publictimelapse_list(request):
    timelapses_list = list(PublicTimelapse.objects.order_by('priority').values())

    page = request.GET.get('page', 1)
    paginator = Paginator(timelapses_list, 9)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'publictimelapse_list.html', dict(timelapses=page_obj.object_list, page_obj=page_obj))
