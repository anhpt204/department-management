from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from dateutil.relativedelta import relativedelta


# Create your models here.
class House(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100)
    address = models.CharField(verbose_name="Address", max_length=500)

    def __str__(self):
        return self.name


class Room(models.Model):
    room_number = models.CharField(verbose_name="Room number", max_length=10)
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, null=True, blank=True)

    max_occupancy = models.PositiveSmallIntegerField(
        verbose_name="Max occupancy", default=3
    )
    electric_device_id = models.CharField(
        verbose_name="Electric Device ID", max_length=50
    )
    door_key = models.PositiveIntegerField(
        verbose_name="Door key",
    )

    status = models.BooleanField(verbose_name="Status", default=True)

    class Meta:
        ordering = [
            "room_number",
        ]

    def __str__(self):
        return self.room_number


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )  # Tham chiếu đến mô hình User của Django
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    cccd = models.TextField("CCCD", null=True, blank=True)
    cccd_image_front = models.ImageField("CCCD Front", null=True, blank=True)
    cccd_image_back = models.ImageField("CCCD Back", null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Electricity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    electricity_reading = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Electricity"
        verbose_name_plural = "Electricities"


class Contract(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    electricity_start_reading = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Chỉ số điện ngày bắt đầu hợp đồng
    occupants = models.PositiveIntegerField()  # Số người ở
    security_deposit = models.PositiveIntegerField()  # Tiền đặt cọc
    rent_fee = models.PositiveIntegerField()  # Tiền thuê phòng
    electricity_fee = models.PositiveIntegerField()
    water_fee = models.PositiveIntegerField()
    internet_fee = models.PositiveIntegerField()
    cleaning_fee = models.PositiveIntegerField()
    charging_fee = models.PositiveIntegerField()
    other_fee = models.PositiveIntegerField(default=0)
    other_fee_desc = models.CharField(max_length=500, null=True, blank=True)
    customers = models.ManyToManyField(Customer, through="ContractCustomer")
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.room.room_number}: {self.start_date} => {self.end_date}"


class ContractCustomer(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)  # Đánh dấu KH chính


class Invoice(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    electricity_start = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_end = models.DecimalField(max_digits=10, decimal_places=2)
    rent_fee = models.PositiveIntegerField(default=0)  # Tiền thuê phòng
    electricity_fee = models.PositiveIntegerField(default=0)
    water_fee = models.PositiveIntegerField(default=0)
    internet_fee = models.PositiveIntegerField(default=0)
    cleaning_fee = models.PositiveIntegerField(default=0)
    charging_fee = models.PositiveIntegerField(default=0)
    other_fee = models.PositiveIntegerField(default=0)
    other_fee_desc = models.CharField(max_length=500, null=True, blank=True)
    previous_debt = models.PositiveIntegerField(default=0)  # Nợ kỳ trước
    paid_amount = models.PositiveIntegerField(default=0)  # Tiền đã tt trong kỳ
    unpaid_amount = models.PositiveIntegerField(default=0)  # Tiền còn thiếu
    total_amount = models.PositiveIntegerField(
        default=0)  # Tổng số tiền trong kỳ
    paid_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ["-invoice_date", "is_paid"]

    def save(self, *args, **kwargs):
        if self.is_paid == False:
            self.update_total_amount()
        else:
            self.paid_amount = self.total_amount
            self.unpaid_amount = 0
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

    def update_total_amount(self):
        self.rent_fee = self.contract.rent_fee
        self.electricity_fee = (
            self.electricity_end - self.electricity_start
        ) * self.contract.electricity_fee
        self.water_fee = self.contract.occupants * self.contract.water_fee
        self.internet_fee = self.contract.internet_fee
        self.cleaning_fee = self.contract.occupants * self.contract.cleaning_fee
        self.charging_fee = self.contract.charging_fee
        self.other_fee = self.contract.other_fee

        self.previous_debt = get_previous_debt(
            current_invoice=self, current_date=self.invoice_date, room=self.contract.room)

        self.total_amount = (
            self.previous_debt
            + self.rent_fee
            + self.electricity_fee
            + self.water_fee
            + self.internet_fee
            + self.cleaning_fee
            + self.charging_fee
            + self.other_fee
        )
        self.unpaid_amount = self.total_amount - self.paid_amount


def get_previous_debt(current_invoice, current_date, room):
    active_contract = room.contract_set.filter(
        start_date__lte=current_date, end_date__gte=current_date
    ).first()
    if active_contract == None:
        return 0

    latest_invoice = active_contract.invoice_set.order_by(
        "-invoice_date"
    ).first()

    if latest_invoice == None:
        return 0
    if current_invoice and latest_invoice.id == current_invoice.id:
        return 0
    return latest_invoice.unpaid_amount

# class Payment(models.Model):
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
#     payment_date = models.DateField()
#     amount = models.IntegerField()  # Số tiền thanh toán


# class Equipment(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     status = models.CharField(max_length=100)

# class Issue(models.Model):
#     equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     description = models.TextField()
#     report_date = models.DateField()
#     resolved = models.BooleanField(default=False)

# class Repair(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
#     description = models.TextField()
#     repair_date = models.DateField()
#     repair_cost = models.IntegerField()  # Chi phí sửa chữa
