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
    #booking_time = forms.TimeField(widget=forms.TimeInput)
    class Meta:
        model=Bookings
        fields=('booking_date','booking_time','booking_duration')
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),            
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'booking_duration': forms.TimeInput(attrs={'type': 'time'}),
        }
        

