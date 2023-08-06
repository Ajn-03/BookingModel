from django.urls import path

from . import views

app_name = 'clovia'
urlpatterns = [
    path("", views.home, name="home"),   
    path("<int:login_id>/", views.Meeting_RoomsView.as_view(), name="meeting_rooms"),
    path("<int:login_id>/<int:rooms_id>/", views.bookings, name="bookings"),    
    path("<int:login_id>/<int:rooms_id>/bookedslots/", views.slots, name="slots"),  
    path("<int:login_id>/meetings/", views.meetings, name="meetings"),
    path("<int:login_id>/bookings/", views.view_bookings, name="view_bookings"),    
    path('<int:login_id>/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('<int:booking_id>/view_participant/', views.view_participants, name='view_participants'),
]