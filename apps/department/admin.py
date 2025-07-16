from collections.abc import Sequence
from django.contrib import admin
from django.http import HttpRequest
from .models import (
    House,
    UserHouse,
    Room,
    Customer,
    Electricity,
    Contract,
    ContractCustomer,
    Invoice,
)

from django.utils.html import format_html


class HouseFilterBase(admin.SimpleListFilter):
    title = 'House'
    parameter_name = 'house'

    # field_name là tên field liên kết đến House (vd: 'house', 'room__house')
    field_name = None

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            houses = House.objects.all()
        else:
            user_houses = UserHouse.objects.filter(
                user=request.user).values_list('house_id', flat=True)
            houses = House.objects.filter(id__in=user_houses)
        return [(h.id, h.name) for h in houses]

    def queryset(self, request, queryset):
        if self.value():
            filter_kwargs = {f"{self.field_name}__id": self.value()}
            return queryset.filter(**filter_kwargs)
        return queryset


class RoomHouseFilter(HouseFilterBase):
    field_name = 'house'


class ContractHouseFilter(HouseFilterBase):
    field_name = 'room__house'


class ElectricityHouseFilter(HouseFilterBase):
    field_name = 'room__house'


class InvoiceHouseFilter(HouseFilterBase):
    field_name = 'contract__room__house'


class CustomerHouseFilter(HouseFilterBase):
    field_name = 'contractcustomer__contract__room__house'


class HouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']

    # Giới hạn danh sách House theo user
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_houses = UserHouse.objects.filter(
            user=request.user).values_list('house_id', flat=True)
        return qs.filter(id__in=user_houses)

    # Nếu user không phải superuser, chỉ cho phép chọn House mà họ quản lý
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "house" and not request.user.is_superuser:
            user_houses = UserHouse.objects.filter(
                user=request.user).values_list('house_id', flat=True)
            kwargs["queryset"] = House.objects.filter(id__in=user_houses)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class UserHouseAdmin(admin.ModelAdmin):
    list_display = ['user', 'house']


class RoomAdmin(admin.ModelAdmin):
    list_display = [
        "room_number",
        "house",
        "max_occupancy",
        "door_key",
        "electric_device_id",
    ]
    list_filter = [RoomHouseFilter,]
    actions = None
    list_editable = [
        "house",
        "door_key",
    ]
    list_display_links = ['room_number']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_houses = UserHouse.objects.filter(
            user=request.user).values_list('house_id', flat=True)
        return qs.filter(house_id__in=user_houses)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "house" and not request.user.is_superuser:
            user_houses = UserHouse.objects.filter(
                user=request.user).values_list('house_id', flat=True)
            kwargs["queryset"] = House.objects.filter(id__in=user_houses)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    list_filter = [CustomerHouseFilter]

    # Giới hạn dữ liệu hiển thị theo House của user
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_houses = UserHouse.objects.filter(
            user=request.user).values_list('house_id', flat=True)
        return qs.filter(contractcustomer__contract__room__house_id__in=user_houses).distinct()


class ElectricityAdmin(admin.ModelAdmin):
    list_display = ["house_name", "room", "date", "electricity_reading"]
    list_filter = [ElectricityHouseFilter, 'room', 'date']

    def house_name(self, obj):
        return obj.room.house

    # Giới hạn dữ liệu theo house mà user được gán

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_houses = UserHouse.objects.filter(
            user=request.user).values_list('house_id', flat=True)
        return qs.filter(room__house_id__in=user_houses)

    # Dropdown chọn Room chỉ hiển thị Room thuộc House mà user có quyền
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room" and not request.user.is_superuser:
            user_houses = UserHouse.objects.filter(
                user=request.user).values_list('house_id', flat=True)
            kwargs["queryset"] = Room.objects.filter(house_id__in=user_houses)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
        ContractHouseFilter,
        "room",
        "published",
    ]

    inlines = [
        ContractCustomerInline,
    ]

    save_as = True

    def house_name(self, obj):
        return obj.room.house

    # Giới hạn dữ liệu theo house mà user được gán
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_houses = UserHouse.objects.filter(
            user=request.user).values_list('house_id', flat=True)
        return qs.filter(room__house_id__in=user_houses)

    # Dropdown chọn Room chỉ hiển thị Room thuộc House mà user có quyền
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room" and not request.user.is_superuser:
            user_houses = UserHouse.objects.filter(
                user=request.user).values_list('house_id', flat=True)
            kwargs["queryset"] = Room.objects.filter(house_id__in=user_houses)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
        # "contract__room__house",
        InvoiceHouseFilter,
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

    # Giới hạn dữ liệu hiển thị theo House của user

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_houses = UserHouse.objects.filter(
            user=request.user).values_list('house_id', flat=True)
        return qs.filter(contract__room__house_id__in=user_houses)

    # Dropdown chọn Contract chỉ hiển thị các hợp đồng trong House của user
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contract" and not request.user.is_superuser:
            user_houses = UserHouse.objects.filter(
                user=request.user).values_list('house_id', flat=True)
            kwargs["queryset"] = Contract.objects.filter(
                room__house_id__in=user_houses)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(House, HouseAdmin)
admin.site.register(UserHouse, UserHouseAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Electricity, ElectricityAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Invoice, InvoiceAdmin)
