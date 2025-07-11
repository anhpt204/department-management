import logging
from .env import (
    ENDPOINT,
    CLIENT_ID,
    CLIENT_SECRET,
)
from tuya_connector import TuyaOpenAPI, TuyaOpenPulsar, TuyaCloudPulsarTopic
from .models import Room, Electricity, Invoice, Contract, get_previous_debt
import datetime
from dateutil.relativedelta import relativedelta
import decimal
from pytz import timezone
from django.utils import timezone as djtz

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


def update_expired_contracts(request):
    try:
        today = datetime.datetime.now().date()
        expired_contracts = Contract.objects.filter(end_date__lt=today)
        for expired_contract in expired_contracts:
            expired_contract.published = False
            expired_contract.save()
        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def update_electricity(request):
    try:
        today = datetime.datetime.now().astimezone(timezone('Asia/Bangkok')).date()
        print('today: ', today)
        rooms = Room.objects.filter()
        for room in rooms:
            print('Room: ', room.room_number)
            # 1. check and get electricity
            electricity = Electricity.objects.filter(
                room=room, date=today).first()
            energy_total = 0
            if electricity is not None:
                energy_total = electricity.electricity_reading

            need_get_electricity = electricity is None

            active_contract = room.contract_set.filter(
                start_date__lte=today, end_date__gte=today
            ).first()

            print('active contract: ', active_contract)

            local_today = datetime.datetime.now().astimezone(timezone('Asia/Bangkok'))
            print('today: ', local_today)

            is_today_billing_day = (
                active_contract != None and local_today.day == active_contract.start_date.day
            )
            need_create_new_invoice = False
            print("today is billing day: ", is_today_billing_day)
            if is_today_billing_day:
                invoice_today = active_contract.invoice_set.filter(
                    invoice_date=today).first()
                print('invoice today: ', invoice_today)
                need_create_new_invoice = invoice_today == None

            if need_get_electricity:
                energy_total, ok = get_electricity(room.electric_device_id)
                print('get electricity ok? ', ok)
                need_create_new_invoice = need_create_new_invoice and ok

                if ok:
                    new_electricity = Electricity(
                        room=room, date=today, electricity_reading=energy_total
                    )
                    new_electricity.save()

            # 2. create invoice if necessary
            print('need create new invoice: ', need_create_new_invoice)
            if need_create_new_invoice:
                electricity_start = active_contract.electricity_start_reading
                is_not_first_invoice = active_contract.invoice_set.first() != None
                previous_debt = get_previous_debt(
                    current_invoice=None, current_date=today, room=room)

                if is_not_first_invoice:
                    last_billing_date = today - relativedelta(months=1)
                    electricity_of_last_billing_date = Electricity.objects.filter(
                        room=room,
                        date=last_billing_date,
                    ).first()

                    if electricity_of_last_billing_date != None:
                        print('electricity of last billing date: ',
                              electricity_of_last_billing_date.electricity_reading)
                        electricity_start = (
                            electricity_of_last_billing_date.electricity_reading
                        )

                new_invoice = Invoice(
                    contract=active_contract,
                    invoice_date=today,
                    electricity_start=electricity_start,
                    electricity_end=energy_total,
                    rent_fee=active_contract.rent_fee,
                    previous_debt=previous_debt,
                    paid_amount=0,
                    is_paid=False,
                    created_at=datetime.datetime.now(tz=djtz.utc),
                    updated_at=datetime.datetime.now(tz=djtz.utc)
                )
                new_invoice.save()
        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
