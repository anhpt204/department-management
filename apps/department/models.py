from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Room(models.Model):
    room_number = models.CharField(verbose_name="Room number", max_length=10)
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
    rent_fee = models.PositiveIntegerField()  # Tiền thuê phòng
    electricity_fee = models.PositiveIntegerField()
    water_fee = models.PositiveIntegerField()
    internet_fee = models.PositiveIntegerField()
    cleaning_fee = models.PositiveIntegerField()
    charging_fee = models.PositiveIntegerField()
    other_fee = models.PositiveIntegerField(default=0)
    other_fee_desc = models.CharField(max_length=500, null=True, blank=True)
    unpaid_amount = models.PositiveIntegerField(default=0)  # Tiền nợ kỳ trước
    total_amount = models.PositiveIntegerField()  # Tổng số tiền trong kỳ


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.IntegerField()  # Số tiền thanh toán


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
