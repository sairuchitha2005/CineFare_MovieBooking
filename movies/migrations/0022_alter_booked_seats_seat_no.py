# Generated by Django 4.2.7 on 2023-11-16 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0021_alter_booked_seats_show'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booked_seats',
            name='seat_no',
            field=models.CharField(max_length=100),
        ),
    ]
