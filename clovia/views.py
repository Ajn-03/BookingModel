from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
# Create your views here.
from .forms import LoginForm,BookingForm,EditForm,ParticipantForm
from django.views import generic
from .models import Login,Meeting_Rooms, Bookings, Notification
from datetime import datetime
from django.db.models import Q
from asgiref.sync import async_to_sync
from django.core.mail import send_mail

@async_to_sync
async def send_email_notification(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)

def extract_name_from_username(username):
    #extract the name part
    local_part=username.split('@')[0]
    #extract first name
    first_name= local_part.split(".")[0]
    first_name = first_name.capitalize()
    return f"{first_name}"

#login page view
def home(request):
    context = {}
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            temp = form.cleaned_data.get("username")
            login=form.save() 
            return redirect("clovia:meeting_rooms", login_id=login.id)
        else:
            context['form'] = form
            return render(request, "clovia/invalid.html", context)
        
    context['form'] = form
    return render(request, "clovia/home.html", context)

#all meeting rooms
class Meeting_RoomsView(generic.ListView):
    template_name = "clovia/meeting_rooms.html"
    context_object_name = "room_list"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_id = self.kwargs.get('login_id')
        
        #we get the username who has logged in
        login = get_object_or_404(Login,pk=login_id)
        #using the function defined above we extract the first name
        name = extract_name_from_username(login.username)      
        context['name'] = name
        context['login']=login
        
        #Delete Past Notifications
        now=datetime.now().date()
        past_bookings=Bookings.objects.filter(booking_date__lt=now)
        for booking in past_bookings:
            past_booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
            if past_booking_datetime < datetime.now():
                notification_criteria = (Q(message__contains=str(booking.booking_date)) & Q(message__contains=str(booking.booking_time)))
                Notification.objects.filter(notification_criteria).delete()
                 
        # Fetch and mark notifications
        notifications = Notification.objects.filter(receiver=login)
        print("Notifications Queryset:", notifications)
        notifications.update(is_read=True)
        context['notifications'] = notifications
        return context

    def get_queryset(self):
        queryset= Meeting_Rooms.objects.all()
        #get the data from the form 
        date = self.request.GET.get('date')
        time = self.request.GET.get('time')

        if date and time:
            #Convert them into datetime objects and filter the meeting rooms based on the provided date and time
            datetime_str = f"{date} {time}"
            booking_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            
            # Get the booked meeting rooms
            booked_rooms = Bookings.objects.filter(
                booking_date=booking_datetime.date(),
                booking_time=booking_datetime.time()
            ).values_list('room_name_id', flat=True)

            # Exclude the booked meeting rooms from the queryset
            queryset = queryset.exclude(id__in=booked_rooms)

        return queryset
    
def bookings(request,login_id,rooms_id):
    login = get_object_or_404(Login,pk=login_id)
    room = get_object_or_404(Meeting_Rooms,pk=rooms_id)
    form = BookingForm()
    context = {'login': login,'room': room}
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            #we get the cleaned data
            participant=form.cleaned_data.get("participants")
            b_date = form.cleaned_data.get("booking_date")
            b_time = form.cleaned_data.get("booking_time")
            e_time = form.cleaned_data.get("end_time")
            context['form'] = form
            # Check if the booking date is in the past
            current_datetime = datetime.now()
            booking_datetime = datetime.combine(b_date, b_time)
            if booking_datetime < current_datetime:
                context['message'] = 'Cannot book in the past!'
                return render(request, 'clovia/booking.html', context)

            #check if end time is before starting time
            if e_time<b_time:
                context['message'] = 'End Time in the past!'
                return render(request, 'clovia/booking.html', context)

            #check if the booking already exists
            if Bookings.objects.filter(room_name=room,booking_date=b_date,booking_time__lte=e_time,end_time__gte=b_time).exists():
                context['message'] = 'Booking already exists!'
                return render(request, 'clovia/booking.html',context)

            else:
                booking = Bookings.objects.create(user=login,room_name=room,booking_date=b_date,booking_time=b_time,end_time=e_time)
                #set participants
                booking.participants.set(participant)
                #send notifications
                for participant_user in participant.all():
                    notification_message = f"{login} has added you as a participant to the meeting on {b_date} at {b_time} in {room.room}."
                    Notification.objects.create(receiver=participant_user, message=notification_message)
                    subject = 'Meeting Invitation'
                    message = notification_message
                    from_email = login
                    recipient_list = [participant_user]
                    send_email_notification(subject, message, from_email, recipient_list)

                context['message'] = 'Booking Successful!'
                return render(request, 'clovia/booking.html',context) 
    
    context['form'] = form
    return render(request, "clovia/booking.html", context)

#booked slots
def slots(request,login_id,rooms_id):
    login = Login.objects.get(pk=login_id)
    room = Meeting_Rooms.objects.get(pk=rooms_id)
    #Delete Past Bookings
    now=datetime.now().date()
    past_bookings=Bookings.objects.filter(booking_date__lt=now)
    for booking in past_bookings:
        past_booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
        if past_booking_datetime < datetime.now():
            Bookings.objects.filter(booking_date=booking.booking_date , booking_time=booking.booking_time).delete()        
    
    query_results = Bookings.objects.filter(room_name=room).order_by("-booking_date")
    return render(request,'clovia/slots.html',{'login': login, 'room': room,'query_results':query_results})

#your meetings
def meetings(request,login_id):
    login = Login.objects.get(pk=login_id)    
    #Delete Past Meetings
    now=datetime.now().date()
    past_bookings=Bookings.objects.filter(booking_date__lt=now)
    for booking in past_bookings:
        past_booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
        if past_booking_datetime < datetime.now():
            booking.delete()        
    
    user_meetings = Bookings.objects.filter(user=login)
    participant_meetings = Bookings.objects.filter(participants=login)
    all_meetings = user_meetings.union(participant_meetings).order_by("-booking_date")
    return render(request,'clovia/meetings.html',{'login': login,'query_results':all_meetings})

#your bookings
def view_bookings(request,login_id):
    login = Login.objects.get(pk=login_id)
    query_results = Bookings.objects.filter(user=login).order_by("-booking_date")
    return render(request,'clovia/view_bookings.html',{'login': login,'query_results':query_results})

#edit bookings
def edit_booking(request, booking_id,login_id):
    booking = get_object_or_404(Bookings, id=booking_id)
    login = Login.objects.get(pk=login_id)
    context = {'login': login,'booking':booking}
    if request.method == 'POST':
        form = EditForm(request.POST, instance=booking)
        if form.is_valid():
            room=form.cleaned_data.get("room_name")
            b_date = form.cleaned_data.get("booking_date")
            b_time = form.cleaned_data.get("booking_time")
            e_time = form.cleaned_data.get("end_time")
            context['form'] = form
            # Check if the booking date is in the past
            current_datetime = datetime.now()
            booking_datetime = datetime.combine(b_date, b_time)
            if booking_datetime < current_datetime:
                context['message'] = 'Cannot book in the past!'
                return render(request, 'clovia/edit_booking.html', context)

            #check if end time is before starting time
            if e_time<b_time:
                context['message'] = 'End Time in the past!'
                return render(request, 'clovia/edit_booking.html', context)

            #check if the booking already exists
            if Bookings.objects.filter(room_name=room,booking_date=b_date,booking_time__lte=e_time,
                                       end_time__gte=b_time).exists():
                context['message'] = 'Booking already exists!'
                return render(request, 'clovia/edit_booking.html',context)
            else:
                form.save()
                return redirect('clovia:view_bookings',login_id=login_id)
    else:
        form = EditForm(instance=booking)

    return render(request, 'clovia/edit_booking.html', {'form': form})


def view_participants(request, booking_id):
    booking = get_object_or_404(Bookings, pk=booking_id)
    participants = booking.participants.all()
    form = ParticipantForm()
    context = {'booking': booking, 'participants': participants}
    if request.method=='POST':
        form = ParticipantForm(request.POST)
        
        #Add Participants
        if form.is_valid():
            participant = form.cleaned_data['participants']
            booking.participants.add(participant)
            
            #send notification
            for participant_user in participants:
                notification_message = f"{booking.user} has added you as a participant to the meeting on {booking.booking_date} at {booking.booking_time} in {booking.room_name.room}."
                Notification.objects.create(receiver=participant_user, message=notification_message)
                subject = 'Meeting Invitation'
                message = notification_message
                from_email = booking.user
                recipient_list = [participant_user]
                send_email_notification(subject, message, from_email, recipient_list)

            return render(request, 'clovia/participants.html',context) 
    
    #Remove Participants
    if 'remove_participant' in request.POST:
        participant_id = request.POST.get('remove_participant')
        participant = get_object_or_404(Login, pk=participant_id)
        booking.participants.remove(participant)
        
        #remove notifications
        notification_criteria = (Q(receiver=participant) & Q(message__contains=booking.user.username) &                                                                      Q(message__contains=str(booking.booking_date)) & Q(message__contains=str(booking.booking_time)) &
                                 Q(message__contains=booking.room_name.room))
        Notification.objects.filter(notification_criteria).delete()
        context['form'] = form
        return render(request, 'clovia/participants.html',context) 
     
    context['form'] = form
    return render(request, 'clovia/participants.html', context)





    
 
