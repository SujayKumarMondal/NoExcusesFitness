from django import forms
from .models import TrainerAttendance, Trainer  # Import the TrainerAttendance model
from django.db import models

class AddTrainerForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    mobile_number = forms.IntegerField()
    email = forms.EmailField()
    
    
class TrainerAttendanceForm(forms.ModelForm):  # Ensure this is a ModelForm
    class Meta:
        model = TrainerAttendance
        fields = ['trainer', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'trainer': forms.Select(attrs={'class': 'form-control'}),
        }