from django import forms
from .models import Login, Bookings
from django.core.exceptions import ValidationError

def validate_username(value):
    if not (value.endswith("@clovia.com") or value.endswith("@purplepanda.in")):
        raise ValidationError("Enter Organization Email Id")
        
class LoginForm(forms.ModelForm):
    username=forms.EmailField(validators=[validate_username])
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Login
        fields = ('username', 'password')
        
class BookingForm(forms.ModelForm):
    class Meta:
        model=Bookings
        fields=('booking_date','booking_time','end_time','participants')
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),            
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        
                
class EditForm(forms.ModelForm):
    class Meta:
        model=Bookings
        fields=('room_name','booking_date','booking_time','end_time')
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),            
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        
class ParticipantForm(forms.Form):
    participants=forms.ModelChoiceField(queryset=Login.objects.all())
    
