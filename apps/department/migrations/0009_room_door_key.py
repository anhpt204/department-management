# Generated by Django 3.2.6 on 2024-05-27 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0008_auto_20240527_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='door_key',
            field=models.PositiveIntegerField(default=123456, verbose_name='Door key'),
            preserve_default=False,
        ),
    ]
