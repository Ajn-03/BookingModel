from django.db import models

# Create your models here.
class Login(models.Model):
    username = models.EmailField(max_length=100,)
    password = models.CharField(max_length=15,)
    def __str__(self):
        return self.username
    
class Meeting_Rooms(models.Model):
    room=models.CharField(max_length=50)
    def __str__(self):
        return self.room
    
class Bookings(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    room_name = models.ForeignKey(Meeting_Rooms, on_delete=models.CASCADE)
    booking_date = models.DateField("Booking On")
    booking_time = models.TimeField("Booking At")
    end_time = models.TimeField("Ends At")#for {self.booking_duration}
    participants = models.ManyToManyField(Login, blank=True,related_name='bookings_participated')

    def __str__(self):
        return f"{self.user.username} booked {self.room_name.room}  on {self.booking_date} at {self.booking_time}"

   