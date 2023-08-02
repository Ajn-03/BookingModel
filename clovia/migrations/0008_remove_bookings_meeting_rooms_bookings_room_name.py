# Generated by Django 4.2.3 on 2023-07-29 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clovia', '0007_remove_meeting_rooms_bookings_bookings_meeting_rooms'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='meeting_rooms',
        ),
        migrations.AddField(
            model_name='bookings',
            name='room_name',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='clovia.meeting_rooms'),
            preserve_default=False,
        ),
    ]
