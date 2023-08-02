from django.test import TestCase

# Create your tests here.
"""import datetime
from django.utils import timezone
from .models import Bookings
from django.urls import reverse

def create_booking(user,room_name,days):
    time=timezone.now()+datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text,pub_date=time)

class BookingsBookingViewTests(TestCase):
    date=datetime.now()-datetime.timedelta(days=1)
    time=timezone.now()-datetime.timedelta(minutes=1)
    booking=Bookings.objects.create(user="xyz@clovia.com",room_name="Room N",booking_date=date,booking_time=time,booking_duration="02:00:00")
    response=self.client.get(reverse("clovia:bookings"))
    self.assertContains(response,"Booking Not Available")
    0015_remove_bookings_booking_duration_bookings_end_time.py
    0016_remove_bookings_end_time_bookings_booking_duration.py
"""

    