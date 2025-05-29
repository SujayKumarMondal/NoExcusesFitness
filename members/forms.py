from django import forms
from .models import Attendance  # Import the Attendance model

class AddMemberForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    mobile_number = forms.IntegerField()
    email = forms.EmailField()

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user', 'date', 'status']