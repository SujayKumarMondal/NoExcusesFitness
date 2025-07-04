from django import forms
from .models import Attendance, Member  # Import the Attendance model
from django.db import models

class AddMemberForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    mobile_number = forms.IntegerField()
    email = forms.EmailField()
    
    
class MemberAttendanceForm(forms.ModelForm):  # Ensure this is a ModelForm
    class Meta:
        model = Attendance
        fields = ['member', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'member': forms.Select(attrs={'class': 'form-control'}),
        }