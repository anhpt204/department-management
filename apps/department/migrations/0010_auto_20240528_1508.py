# Generated by Django 3.2.6 on 2024-05-28 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0009_room_door_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='paid_amount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='invoice',
            name='paid_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='previous_debt',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
    ]
