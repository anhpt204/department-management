from django.shortcuts import render
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Invoice, Contract
from dateutil.relativedelta import relativedelta


# Create your views here.
def show_invoice_detail(request, invoice_pk):
    invoice = Invoice.objects.get(pk=invoice_pk)
    contract = invoice.contract
    services = [
        [1, "Tiền phòng", 1, contract.rent_fee, invoice.rent_fee],
        [2, "Internet", 1, contract.internet_fee, invoice.internet_fee],
        [
            3,
            "Nước sinh hoạt",
            contract.occupants,
            contract.water_fee,
            invoice.water_fee,
        ],
        [
            4,
            "Vệ sinh chung",
            contract.occupants,
            contract.cleaning_fee,
            invoice.cleaning_fee,
        ],
    ]
    counter = 4

    if invoice.charging_fee > 0:
        counter += 1
        services.append(
            [
                counter,
                "Sạc xe điện",
                1,
                contract.charging_fee,
                invoice.charging_fee,
            ]
        )

    electricity = invoice.electricity_end - invoice.electricity_start
    counter += 1
    services.append(
        [
            counter,
            "Tiền điện",
            f"{electricity} ({invoice.electricity_end}-{invoice.electricity_start})",
            contract.electricity_fee,
            invoice.electricity_fee,
        ]
    )

    if invoice.other_fee > 0:
        counter += 1
        services.append(
            [
                counter,
                "Khác",
                contract.other_fee_desc,
                contract.other_fee,
                invoice.other_fee,
            ]
        )

    context = {
        "services": services,
        "invoice": invoice,
        "contract": invoice.contract,
        "end_date": invoice.invoice_date + relativedelta(months=1),
        # "electricity": electricity,
    }
    html_template = loader.get_template("department/invoice.html")
    return HttpResponse(html_template.render(context, request))
