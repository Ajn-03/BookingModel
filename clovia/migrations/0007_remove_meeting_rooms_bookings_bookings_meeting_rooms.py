# Generated by Django 4.2.3 on 2023-07-28 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clovia', '0006_remove_bookings_room_name_meeting_rooms_bookings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting_rooms',
            name='bookings',
        ),
        migrations.AddField(
            model_name='bookings',
            name='meeting_rooms',
            field=models.ManyToManyField(to='clovia.meeting_rooms'),
        ),
    ]
