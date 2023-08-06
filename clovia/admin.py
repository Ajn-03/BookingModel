from django.contrib import admin

# Register your models here.
from .models import Login,Meeting_Rooms,Bookings, Notification

admin.site.register(Login)
admin.site.register(Meeting_Rooms)
admin.site.register(Bookings)
admin.site.register(Notification)
