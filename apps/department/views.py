from django.shortcuts import render
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Invoice, Contract
from dateutil.relativedelta import relativedelta


# Create your views here.
def show_invoice_detail(request, invoice_pk):
    invoice = Invoice.objects.get(pk=invoice_pk)
    context = {
        "invoice": invoice,
        "contract": invoice.contract,
        "end_date": invoice.invoice_date + relativedelta(months=1),
        "electricity": invoice.electricity_end - invoice.electricity_start,
    }
    html_template = loader.get_template("department/invoice.html")
    return HttpResponse(html_template.render(context, request))
