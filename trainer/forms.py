from django import forms
from .models import Trainer, TrainerAttendance  # Import the Attendance model
from django.db import models

class TrainerAttendanceForm(forms.ModelForm):  # Ensure this is a ModelForm
    class Meta:
        model = TrainerAttendance
        fields = ['trainer', 'date', 'status']
        # widgets = {
        #     'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        #     'status': forms.Select(attrs={'class': 'form-control'}),
        #     'trainer': forms.Select(attrs={'class': 'form-control'}),
        # }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['trainer'].queryset = Trainer.objects.all()