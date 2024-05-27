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
            need_get_electricity = electricity is None

            active_contract = room.contract_set.filter(
                start_date__lte=today, end_date__gte=today
            ).first()
            is_today_billing_day = (
                active_contract != None and today.day == active_contract.start_date.day
            )
            need_create_new_invoice = is_today_billing_day and need_get_electricity

            if need_get_electricity:
                energy_total, ok = get_electricity(room.electric_device_id)
                print(
                    f"{datetime.datetime.now()}: read electricity of room {room.room_number}, success?: {ok}"
                )
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

                electricity_fee = (
                    energy_total - electricity_start
                ) * active_contract.electricity_fee
                water_fee = active_contract.occupants * active_contract.water_fee
                internet_fee = active_contract.internet_fee
                cleaning_fee = active_contract.occupants * active_contract.cleaning_fee
                charging_fee = active_contract.charging_fee
                other_fee = active_contract.other_fee

                total_amount = (
                    active_contract.rent_fee
                    + electricity_fee
                    + water_fee
                    + internet_fee
                    + cleaning_fee
                    + charging_fee
                    + other_fee
                )

                new_invoice = Invoice(
                    contract=active_contract,
                    invoice_date=today,
                    electricity_start=electricity_start,
                    electricity_end=energy_total,
                    rent_fee=active_contract.rent_fee,
                    electricity_fee=electricity_fee,
                    water_fee=water_fee,
                    internet_fee=internet_fee,
                    cleaning_fee=cleaning_fee,
                    charging_fee=charging_fee,
                    other_fee=other_fee,
                    total_amount=total_amount,
                )
                new_invoice.save()
        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": "str(e)"}, status=500)
