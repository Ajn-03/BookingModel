from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
# Create your views here.
from .forms import LoginForm,BookingForm
from django.views import generic
from .models import Login,Meeting_Rooms, Bookings
from datetime import datetime
from django.db.models import Q

def extract_name_from_username(username):
    #extract the name part
    local_part=username.split('@')[0]
    #extract first name
    first_name= local_part.split(".")[0]
    first_name = first_name.capitalize()
    return f"{first_name}"

def home(request):#login page view
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

class Meeting_RoomsView(generic.ListView):#all meeting rooms
    template_name = "clovia/meeting_rooms.html"
    context_object_name = "room_list"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        login_id = self.kwargs.get('login_id')
        login = get_object_or_404(Login,pk=login_id) #we get the username who has logged in
        name = extract_name_from_username(login.username)#using the function defined above we extract the first name
        context['name'] = name
        context['login']=login
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
                context['message'] = 'Booking Successful!'
                return render(request, 'clovia/booking.html',context) 
    
    context['form'] = form
    return render(request, "clovia/booking.html", context)

def slots(request,login_id,rooms_id):#booked slots
    login = Login.objects.get(pk=login_id)
    room = Meeting_Rooms.objects.get(pk=rooms_id)
    query_results = Bookings.objects.filter(room_name=room).order_by("-booking_date")
    return render(request,'clovia/slots.html',{'login': login, 'room': room,'query_results':query_results})

def meetings(request,login_id):#your meetings
    login = Login.objects.get(pk=login_id)
    user_meetings = Bookings.objects.filter(user=login).order_by("-booking_date")
    participant_meetings = Bookings.objects.filter(user=login).order_by("-booking_date")
    all_meetings = user_meetings | participant_meetings
    return render(request,'clovia/meetings.html',{'login': login,'query_results':all_meetings})

def view_bookings(request,login_id):#your bookings
    login = Login.objects.get(pk=login_id)
    query_results = Bookings.objects.filter(user=login).order_by("-booking_date")
    return render(request,'clovia/view_bookings.html',{'login': login,'query_results':query_results})

def edit_booking(request, booking_id,login_id):
    booking = get_object_or_404(Bookings, id=booking_id)
    login = Login.objects.get(pk=login_id)
    context = {'login': login,'booking':booking}
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
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
            if Bookings.objects.filter(id=booking_id,booking_date=b_date,booking_time__lte=e_time,end_time__gte=b_time).exists():
                context['message'] = 'Booking already exists!'
                return render(request, 'clovia/edit_booking.html',context)
            else:
                form.save()
                return redirect('clovia:view_bookings',login_id=login_id)
    else:
        form = BookingForm(instance=booking)

    return render(request, 'clovia/edit_booking.html', {'form': form})

"""def add_participant(request, booking_id,login_id):
    booking = get_object_or_404(Bookings, id=booking_id)
    login = Login.objects.get(pk=login_id)

    if request.method == 'POST':
        participant_email = request.POST.get('participant_email')
        participant = get_object_or_404(Login, username=participant_email)
        booking.participants.add(participant)
        # Redirect to a success page or the updated booking details page.
        return redirect('clovia:view_bookings',login_id=login_id)

    return render(request, 'clovia/add_participant.html', {'booking': booking})


def remove_participant(request, booking_id,login_id):
    booking = get_object_or_404(Bookings, id=booking_id)
    login = Login.objects.get(pk=login_id)

    if request.method == 'POST':
        participant_email = request.POST.get('participant_email')
        participant = get_object_or_404(Login, username=participant_email)
        booking.participants.remove(participant)
        # Redirect to a success page or the updated booking details page.
        return redirect('clovia:view_bookings',login_id=login_id)

    return render(request, 'clovia/add_participant.html', {'booking': booking})

def remove_participant(request, booking_id, participant_id,login_id):
    booking = get_object_or_404(Bookings, id=booking_id)
    participant = get_object_or_404(Login, id=participant_id)
    login = Login.objects.get(pk=login_id)

    if request.method == 'POST':
        booking.participants.remove(participant)
        # Redirect to a success page or the updated booking details page.
        return redirect('clovia:view_bookings',login_id=login_id)

    return render(request, 'clovia/remove_participant.html', {'booking': booking, 'participant': participant})"""


    
 
