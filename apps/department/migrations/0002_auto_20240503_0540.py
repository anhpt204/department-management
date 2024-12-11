# Generated by Django 3.2.6 on 2024-05-03 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='other_fee',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='contract',
            name='other_fee_desc',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
