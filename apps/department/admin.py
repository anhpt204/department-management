from collections.abc import Sequence
from django.contrib import admin
from django.http import HttpRequest
from .models import (
    House,
    Room,
    Customer,
    Electricity,
    Contract,
    ContractCustomer,
    Invoice,
)

from django.utils.html import format_html


class HouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']


class RoomAdmin(admin.ModelAdmin):
    list_display = [
        "room_number",
        "house",
        "max_occupancy",
        "door_key",
        "electric_device_id",
    ]
    list_filter = ['house',]
    actions = None
    list_editable = [
        "door_key",
    ]
    list_display_links = ['room_number']


class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "name",
        "email",
        "phone",
        "address",
        "cccd",
        "cccd_image_front",
        "cccd_image_back",
    ]
    search_fields = ("name", "phone", "cccd")


class ElectricityAdmin(admin.ModelAdmin):
    list_display = ["house_name", "room", "date", "electricity_reading"]
    list_filter = ['room__house', 'room', 'date']

    def house_name(self, obj):
        return obj.room.house


class ContractCustomerInline(admin.TabularInline):
    model = ContractCustomer
    autocomplete_fields = ("customer",)
    max_num = 5
    extra = 1


class ContractAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Room info",
            {
                "fields": (
                    "room",
                    "occupants",
                    "security_deposit",
                    "electricity_start_reading",
                )
            },
        ),
        ("Date", {"fields": ("start_date", "end_date", "published")}),
        (
            "Service fees",
            {
                "fields": (
                    "rent_fee",
                    "electricity_fee",
                    "water_fee",
                    "internet_fee",
                    "cleaning_fee",
                    "charging_fee",
                    "other_fee",
                    "other_fee_desc",
                )
            },
        ),
    ]

    list_display = [
        "room",
        "house_name",
        "start_date",
        "end_date",
        "published",
        "electricity_start_reading",
        "occupants",
        "security_deposit",
        "rent_fee",
        "electricity_fee",
        "water_fee",
        "internet_fee",
        "cleaning_fee",
        "charging_fee",
        "other_fee",
        "other_fee_desc",
    ]

    list_filter = [
        "room__house",
        "room",
        "published",
    ]

    inlines = [
        ContractCustomerInline,
    ]

    save_as = True

    def house_name(self, obj):
        return obj.room.house


class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "contract",
        "house_name",
        "invoice_date",
        "electricity_start",
        "electricity_end",
        "previous_debt",
        "total_amount",
        "paid_amount",
        "unpaid_amount",
        "is_paid",
        "show_invoice",
        "created_at",
        "updated_at"
    ]
    list_filter = [
        "contract__room__house",
        "contract__room",
        "is_paid",
    ]
    # list_editable = ['is_paid',]
    # readonly_fields = (
    #     "contract",
    #     "invoice_date",
    #     "electricity_start",
    #     # "electricity_end",
    #     "rent_fee",
    #     "electricity_fee",
    #     "water_fee",
    #     "internet_fee",
    #     "cleaning_fee",
    #     "charging_fee",
    #     "other_fee",
    #     "other_fee_desc",
    #     "unpaid_amount",
    #     "total_amount",
    # )
    fieldsets = [
        (
            None,
            {"fields": ["contract", "invoice_date"]},
        ),
        (
            "Electricity",
            {"fields": ["electricity_start", "electricity_end"]},
        ),
        (
            "Fee",
            {
                "fields": [
                    "rent_fee",
                    "electricity_fee",
                    "water_fee",
                    "internet_fee",
                    "cleaning_fee",
                    "charging_fee",
                    "other_fee",
                    "other_fee_desc",
                ]
            },
        ),
        (
            "Payment",
            {
                "fields": [
                    "paid_amount",
                    "previous_debt",
                    "unpaid_amount",
                    "total_amount",
                    "is_paid",
                ]
            },
        ),
    ]

    def show_invoice(self, obj):
        return format_html('<a href="/department/invoices/%d/"> Show </a>' % (obj.pk))

    def house_name(self, obj):
        return obj.contract.room.house


admin.site.register(House, HouseAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Electricity, ElectricityAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Invoice, InvoiceAdmin)
