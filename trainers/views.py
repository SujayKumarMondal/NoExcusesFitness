from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import AddTrainerForm, Trainer, SearchForm, UpdateTrainerGymForm, UpdateTrainerInfoForm, TrainerAttendance
from .forms import TrainerAttendanceForm
import datetime
import csv
import dateutil.relativedelta as delta
import dateutil.parser as parser
from django.core.files.storage import FileSystemStorage
from payments.models import Payments
from trainers_payments.models import TrainerPayments
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from notifications.config import get_notification_count, my_handler
from django.db.models.signals import post_save
from django.contrib import messages

def model_save(model):
    post_save.disconnect(my_handler, sender=Trainer)
    model.save()
    post_save.connect(my_handler, sender=Trainer)

def check_status(request, obj):
    obj.stop = 1 if request.POST.get('stop') == '1' else 0
    return obj

# Export Trainer information.
def export_all(user_obj):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['First name', 'Last name', 'Mobile', 'Admission Date', 'Subscription Type', 'Batch'])
    trainers = user_obj.values_list('first_name', 'last_name', 'mobile_number', 'admitted_on', 'subscription_type', 'batch')
    first_name, last_name = '', ''
    for trainer in trainers:
        first_name = trainer[0]
        last_name = trainer[1]
        writer.writerow(trainer)
    response['Content-Disposition'] = f'attachment; filename="{first_name} {last_name}.csv"'
    return response

def trainers(request):
    form = AddTrainerForm()
    context = {
        'form': form,
        'subs_end_today_count': get_notification_count(),
    }
    return render(request, 'add_trainer.html', context)

def view_trainer(request):
    view_all = Trainer.objects.filter(stop=0).order_by('first_name')
    paginator = Paginator(view_all, 100)
    try:
        page = request.GET.get('page', 1)
        view_all = paginator.page(page)
    except PageNotAnInteger:
        view_all = paginator.page(1)
    except EmptyPage:
        view_all = paginator.page(paginator.num_pages)
    search_form = SearchForm()
    evening = Trainer.objects.filter(batch='evening', stop=0).order_by('first_name')
    morning = Trainer.objects.filter(batch='morning', stop=0).order_by('first_name')
    stopped = Trainer.objects.filter(stop=1).order_by('first_name')
    context = {
        'all': view_all,
        'morning': morning,
        'evening': evening,
        'stopped': stopped,
        'search_form': search_form,
        'subs_end_today_count': get_notification_count(),
    }
    return render(request, 'view_trainer.html', context)

def add_trainer(request):
    success = None
    trainer = None
    if request.method == 'POST':
        form = AddTrainerForm(request.POST, request.FILES)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.first_name = request.POST.get('first_name', '').capitalize()
            temp.last_name = request.POST.get('last_name', '').capitalize()
            temp.registration_upto = parser.parse(request.POST.get('registration_date')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
            if request.POST.get('fee_status') == 'unpaid':
                temp.notification = 1
            model_save(temp)
            success = 'Successfully Added Trainer'
            if temp.fee_status == 'paid':
                payments = TrainerPayments(
                    user=temp,
                    payment_date=temp.registration_date,
                    payment_period=temp.subscription_period,
                    payment_amount=temp.amount
                )
                payments.save()
            trainer = Trainer.objects.last()
        context = {
            'add_success': success,
            'form': form,
            'trainer': trainer,
            'subs_end_today_count': get_notification_count(),
        }
        return render(request, 'add_trainer.html', context)
    else:
        form = AddTrainerForm()
        context = {
            'form': form,
            'subs_end_today_count': get_notification_count(),
        }
    return render(request, 'add_trainer.html', context)

def search_trainer(request):
    if request.method == 'POST':
        if 'clear' in request.POST:
            return redirect('view_trainer')
        search_form = SearchForm(request.POST)
        result = None
        if search_form.is_valid():
            first_name = request.POST.get('search', '')
            result = Trainer.objects.filter(first_name__icontains=first_name)
        view_all = Trainer.objects.all()
        evening = Trainer.objects.filter(batch='evening')
        morning = Trainer.objects.filter(batch='morning')
        context = {
            'all': view_all,
            'morning': morning,
            'evening': evening,
            'search_form': search_form,
            'result': result,
            'subs_end_today_count': get_notification_count(),
        }
        return render(request, 'view_trainer.html', context)
    else:
        search_form = SearchForm()
    return render(request, 'view_trainer.html', {'search_form': search_form})

def delete_trainer(request, id):
    Trainer.objects.filter(pk=id).delete()
    return redirect('view_trainer')

def update_trainer(request, id):
    trainer = get_object_or_404(Trainer, pk=id)
    if request.method == 'POST' and request.POST.get('export'):
        return export_all(Trainer.objects.filter(pk=id))
    if request.method == 'POST' and request.POST.get('no'):
        return redirect('/')
    if request.method == 'POST' and request.POST.get('gym_membership'):
        gym_form = UpdateTrainerGymForm(request.POST)
        if gym_form.is_valid():
            obj = trainer
            amount = request.POST.get('amount')
            # status stopped check
            if obj.stop == 1 and not request.POST.get('stop') == '0' and request.POST.get('gym_membership'):
                messages.error(request, 'Please start the status of trainer to update the record')
                return redirect('update_trainer', id=obj.pk)
            elif obj.batch != request.POST.get('batch'):
                obj.batch = request.POST.get('batch')
                obj = check_status(request, obj)
                model_save(obj)
            elif (datetime.datetime.strptime(str(obj.registration_date), "%Y-%m-%d") != datetime.datetime.strptime(request.POST.get('registration_date'), "%Y-%m-%d")):
                obj.registration_date = parser.parse(request.POST.get('registration_date'))
                obj.registration_upto = parser.parse(request.POST.get('registration_date')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                obj.fee_status = request.POST.get('fee_status')
                obj = check_status(request, obj)
                model_save(obj)
            elif (str(obj.amount) != str(amount)) and (str(obj.subscription_period) != str(request.POST.get('subscription_period'))):
                obj.subscription_type = request.POST.get('subscription_type')
                obj.subscription_period = request.POST.get('subscription_period')
                obj.registration_date = parser.parse(request.POST.get('registration_upto'))
                obj.registration_upto = parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                obj.fee_status = request.POST.get('fee_status')
                obj.amount = request.POST.get('amount')
                obj = check_status(request, obj)
                model_save(obj)
            elif (str(obj.subscription_period) != str(request.POST.get('subscription_period'))):
                obj.subscription_period = request.POST.get('subscription_period')
                obj = check_status(request, obj)
                model_save(obj)
            elif (str(obj.amount) != str(amount)) and (obj.subscription_type != request.POST.get('subscription_type')):
                obj.subscription_type = request.POST.get('subscription_type')
                obj.subscription_period = request.POST.get('subscription_period')
                obj.registration_date = parser.parse(request.POST.get('registration_upto'))
                obj.registration_upto = parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                obj.fee_status = request.POST.get('fee_status')
                obj.amount = request.POST.get('amount')
                obj = check_status(request, obj)
                model_save(obj)
            elif (str(obj.amount) != str(amount)) and ((request.POST.get('fee_status') == 'paid') or (request.POST.get('fee_status') == 'pending')):
                obj.amount = amount
                obj.fee_status = request.POST.get('fee_status')
                obj = check_status(request, obj)
                model_save(obj)
            elif (str(obj.amount) != str(amount)):
                obj.registration_date = parser.parse(request.POST.get('registration_upto'))
                obj.registration_upto = parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                obj.fee_status = request.POST.get('fee_status')
                obj.amount = request.POST.get('amount')
                if request.POST.get('fee_status') == 'pending':
                    obj.notification = 1
                elif request.POST.get('fee_status') == 'paid':
                    obj.notification = 2
                obj = check_status(request, obj)
                model_save(obj)
            else:
                if not request.POST.get('stop') == '1':
                    obj.registration_date = parser.parse(request.POST.get('registration_upto'))
                    obj.registration_upto = parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    obj.amount = request.POST.get('amount')
                    if request.POST.get('fee_status') == 'unpaid':
                        obj.notification = 1
                    elif request.POST.get('fee_status') == 'paid':
                        obj.notification = 2
                obj.fee_status = request.POST.get('fee_status')
                obj = check_status(request, obj)
                model_save(obj)
            # Add payments if payment is 'paid'
            if obj.fee_status == 'paid':
                check = TrainerPayments.objects.filter(
                    payment_date=obj.registration_date,
                    user__pk=obj.pk).count()
                if check == 0:
                    payments = TrainerPayments(
                        user=obj,
                        payment_date=obj.registration_date,
                        payment_period=obj.subscription_period,
                        payment_amount=obj.amount)
                    payments.save()
            user = Trainer.objects.get(pk=id)
            gym_form = UpdateTrainerGymForm(initial={
                'registration_date': user.registration_date,
                'registration_upto': user.registration_upto,
                'subscription_type': user.subscription_type,
                'subscription_period': user.subscription_period,
                'amount': user.amount,
                'fee_status': user.fee_status,
                'batch': user.batch,
                'stop': user.stop,
            })
            info_form = UpdateTrainerInfoForm(initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'dob': user.dob,
            })
            try:
                payments = TrainerPayments.objects.filter(user=user)
            except TrainerPayments.DoesNotExist:
                payments = 'No Records'
            messages.success(request, 'Record updated successfully!')
            return redirect('update_trainer', id=user.pk)
        else:
            user = Trainer.objects.get(pk=id)
            gym_form = UpdateTrainerGymForm(initial={
                'registration_date': user.registration_date,
                'registration_upto': user.registration_upto,
                'subscription_type': user.subscription_type,
                'subscription_period': user.subscription_period,
                'amount': user.amount,
                'fee_status': user.fee_status,
                'batch': user.batch,
                'stop': user.stop,
            })
            info_form = UpdateTrainerInfoForm(initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'dob': user.dob,
            })
            try:
                payments = TrainerPayments.objects.filter(user=user)
            except TrainerPayments.DoesNotExist:
                payments = 'No Records'
            return render(request, 'trainer_update.html', {
                'payments': payments,
                'gym_form': gym_form,
                'info_form': info_form,
                'user': user,
                'subs_end_today_count': get_notification_count(),
            })
    elif request.method == 'POST' and request.POST.get('info'):
        obj = trainer
        obj.first_name = request.POST.get('first_name')
        obj.last_name = request.POST.get('last_name')
        obj.dob = request.POST.get('dob')
        if 'photo' in request.FILES:
            myfile = request.FILES['photo']
            fs = FileSystemStorage(base_url="")
            photo = fs.save(myfile.name, myfile)
            obj.photo = fs.url(photo)
        model_save(obj)
        user = Trainer.objects.get(pk=id)
        gym_form = UpdateTrainerGymForm(initial={
            'registration_date': user.registration_date,
            'registration_upto': user.registration_upto,
            'subscription_type': user.subscription_type,
            'subscription_period': user.subscription_period,
            'amount': user.amount,
            'fee_status': user.fee_status,
            'batch': user.batch,
            'stop': user.stop,
        })
        info_form = UpdateTrainerInfoForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'dob': user.dob,
        })
        try:
            payments = TrainerPayments.objects.filter(user=user)
        except TrainerPayments.DoesNotExist:
            payments = 'No Records'
        return render(request, 'trainer_update.html', {
            'payments': payments,
            'gym_form': gym_form,
            'info_form': info_form,
            'user': user,
            'updated': 'Record Updated Successfully',
            'subs_end_today_count': get_notification_count(),
        })
    else:
        user = Trainer.objects.get(pk=id)
        if TrainerPayments.objects.filter(user=user).exists():
            payments = TrainerPayments.objects.filter(user=user)
        else:
            payments = 'No Records'
        gym_form = UpdateTrainerGymForm(initial={
            'registration_date': user.registration_date,
            'registration_upto': user.registration_upto,
            'subscription_type': user.subscription_type,
            'subscription_period': user.subscription_period,
            'amount': user.amount,
            'fee_status': user.fee_status,
            'batch': user.batch,
            'stop': user.stop,
        })
        info_form = UpdateTrainerInfoForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'dob': user.dob,
        })
        return render(request, 'trainer_update.html', {
            'payments': payments,
            'gym_form': gym_form,
            'info_form': info_form,
            'user': user,
            'subs_end_today_count': get_notification_count(),
        })

def attendance_view(request):
    if request.method == 'POST':
        form = TrainerAttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('trainer_attendance')
    else:
        form = TrainerAttendanceForm()
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

def edit_attendance(request, id):
    record = get_object_or_404(TrainerAttendance, id=id)
    if request.method == 'POST':
        form = TrainerAttendanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('trainer_attendance')
    else:
        form = TrainerAttendanceForm(instance=record)
    return render(request, 'edit_attendance.html', {'form': form, 'record': record})

def delete_attendance(request, record_id):
    record = get_object_or_404(TrainerAttendance, id=record_id)
    record.delete()
    return redirect('trainer_attendance')

def trainer(request):
    return render(request, 'trainer.html')