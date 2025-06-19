from django.shortcuts import get_object_or_404, render, redirect
from .models import Trainer
from .models import TrainerAttendance
from .forms import TrainerAttendanceForm
def trainer_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        reg_date = request.POST['reg_date']
        reg_upto = request.POST['reg_upto']
        sub_type = request.POST['sub_type']
        sub_period = request.POST['sub_period']
        fees_amount = request.POST['fees_amount']
        fees_status = request.POST['fees_status']

        Trainer.objects.create(
            name=name,
            dob=dob,
            reg_date=reg_date,
            reg_upto=reg_upto,
            sub_type=sub_type,
            sub_period=sub_period,
            fees_amount=fees_amount,
            fees_status=fees_status,
        )
        return redirect('trainer')

    trainers = Trainer.objects.all()
    return render(request, 'trainer.html', {'trainers': trainers})


def edit_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)

    if request.method == 'POST':
        # update trainer data
        trainer.name = request.POST['name']
        trainer.dob = request.POST['dob']
        trainer.reg_date = request.POST['reg_date']
        trainer.reg_upto = request.POST['reg_upto']
        trainer.sub_type = request.POST['sub_type']
        trainer.sub_period = request.POST['sub_period']
        trainer.fees_amount = request.POST['fees_amount']
        trainer.fees_status = request.POST['fees_status']
        trainer.save()
        return redirect('trainer')

    return render(request, 'edit_trainer.html', {'trainer': trainer})


def delete_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    if request.method == 'POST':
        trainer.delete()
        return redirect('trainer')
    return redirect('trainer')


def trainer_attendance_view(request):
    if request.method == 'POST':
        form = TrainerAttendanceForm(request.POST)
        if form.is_valid():
            form.save()  # Save the attendance record
            return redirect('trainer_attendance')
    else:
        form = TrainerAttendanceForm()

    # Filter attendance records by date if filter_date is provided
    filter_date = request.GET.get('filter_date')
    if filter_date:
        attendance_records = TrainerAttendance.objects.filter(date=filter_date)
    else:
        attendance_records = TrainerAttendance.objects.all()

    context = {
        'form': form,
        'attendance_records': attendance_records,
        'filter_date': filter_date,
    }
    return render(request, 'trainer_attendance.html', context)


def edit_trainer_attendance(request, id):
    # Fetch the attendance record
    record = get_object_or_404(TrainerAttendance, id=id)
    
    if request.method == 'POST':
        # Bind the form with POST data and the existing record
        form = TrainerAttendanceForm(request.POST, instance=record)
        if form.is_valid():
            # Save the updated record
            form.save()
            # Redirect to the attendance page
            return redirect('trainer_attendance')  # Replace 'attendance' with the correct URL name
    else:
        # Initialize the form with the existing record
        form = TrainerAttendanceForm(instance=record)
    
    # Render the edit template with the form and record
    return render(request, 'edit_trainer_attendance.html', {'form': form, 'record': record})

def delete_trainer_attendance(request, record_id):
    record = get_object_or_404(TrainerAttendance, id=record_id)
    record.delete()
    return redirect('trainer_attendance')

def trainer(request):
    return render(request, 'trainer.html')