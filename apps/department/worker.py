import logging
from .env import (
    ENDPOINT,
    CLIENT_ID,
    CLIENT_SECRET,
)
from tuya_connector import TuyaOpenAPI, TuyaOpenPulsar, TuyaCloudPulsarTopic
from .models import Room, Electricity, Invoice
import datetime
from dateutil.relativedelta import relativedelta
import decimal

from django.http import JsonResponse

openapi = TuyaOpenAPI(ENDPOINT, CLIENT_ID, CLIENT_SECRET)
openapi.connect()


def get_electricity(device_id):

    resp = openapi.get(f"/v1.0/iot-03/devices/{device_id}/status")

    if resp["success"] != True:
        return 0, False

    result = resp["result"]
    for item in result:
        if item["code"] == "forward_energy_total":
            energy_total = item["value"]
            energy_total = decimal.Decimal(energy_total / 100.0)
            return energy_total, True

    # print(resp)


def update_electricity(request):
    try:
        today = datetime.datetime.now().date()
        rooms = Room.objects.filter()
        for room in rooms:
            # 1. check and get electricity
            electricity = Electricity.objects.filter(room=room, date=today).first()
            energy_total = 0
            if electricity is not None:
                energy_total = electricity.electricity_reading

            need_get_electricity = electricity is None

            active_contract = room.contract_set.filter(
                start_date__lte=today, end_date__gte=today
            ).first()
            is_today_billing_day = (
                active_contract != None and today.day == active_contract.start_date.day
            )
            need_create_new_invoice = is_today_billing_day

            if need_get_electricity:
                energy_total, ok = get_electricity(room.electric_device_id)
                need_create_new_invoice = need_create_new_invoice and ok

                if ok:
                    new_electricity = Electricity(
                        room=room, date=today, electricity_reading=energy_total
                    )
                    new_electricity.save()

            # 2. create invoice if necessary
            if need_create_new_invoice:
                electricity_start = active_contract.electricity_start_reading
                is_not_first_invoice = active_contract.invoice_set.first() != None
                previous_debt = 0

                if is_not_first_invoice:
                    last_billing_date = today - relativedelta(months=1)
                    electricity_of_last_billing_date = Electricity.objects.filter(
                        room=room,
                        date=last_billing_date,
                    ).first()

                    if electricity_of_last_billing_date == None:
                        break

                    electricity_start = (
                        electricity_of_last_billing_date.electricity_reading
                    )

                    latest_invoice = active_contract.invoice_set.order_by(
                        "-invoice_date"
                    ).first()
                    previous_debt = latest_invoice.unpaid_amount

                new_invoice = Invoice(
                    contract=active_contract,
                    invoice_date=today,
                    electricity_start=electricity_start,
                    electricity_end=energy_total,
                    rent_fee=active_contract.rent_fee,
                    previous_debt=previous_debt,
                    paid_amount=0,
                    is_paid=False,
                )
                new_invoice.save()
        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
