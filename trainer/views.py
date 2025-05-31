from django.shortcuts import get_object_or_404, render, redirect
from .models import Trainer

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