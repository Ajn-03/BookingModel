# Generated by Django 4.2.3 on 2023-08-02 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clovia', '0015_remove_bookings_booking_duration_bookings_end_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='booking_duration',
        ),
    ]
