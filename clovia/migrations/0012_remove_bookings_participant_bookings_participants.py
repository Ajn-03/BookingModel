# Generated by Django 4.2.3 on 2023-07-31 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clovia', '0011_bookings_participant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='participant',
        ),
        migrations.AddField(
            model_name='bookings',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='bookings_participated', to='clovia.login'),
        ),
    ]
