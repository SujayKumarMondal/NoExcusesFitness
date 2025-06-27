from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.core import serializers
from .models import AddTrainerForm, Trainer, SearchForm, UpdateTrainerGymForm, UpdateTrainerInfoForm
import datetime, csv
from django.http import HttpResponse
import dateutil.relativedelta as delta
import dateutil.parser as parser
from django.core.files.storage import FileSystemStorage
from payments.models import Payments
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from notifications.config import get_notification_count
from django.db.models.signals import post_save
from notifications.config import my_handler
from django.contrib import messages
from .models import TrainerAttendance
from .forms import TrainerAttendanceForm
from django.shortcuts import get_object_or_404, redirect, render

def model_save(model):
    post_save.disconnect(my_handler, sender=Trainer)
    model.save()
    post_save.connect(my_handler, sender=Trainer)

def check_status(request, object):
    object.stop = 1 if request.POST.get('stop') == '1' else 0
    return object

# Export user information.
def export_all(user_obj):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['First name', 'Last name', 'Mobile', 'Admission Date', 'Subscription Type', 'Batch'])
    trainers = user_obj.values_list('first_name', 'last_name', 'mobile_number', 'admitted_on', 'subscription_type', 'batch')
    for user in trainers:
        first_name = user[0]
        last_name = user[1]
        writer.writerow(user)

    response['Content-Disposition'] = 'attachment; filename="' + first_name + ' ' + last_name + '.csv"'
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
    # get all trainers according to their batches
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
            # Save the new trainer
            temp = form.save(commit=False)
            temp.first_name = request.POST.get('first_name').capitalize()
            temp.last_name = request.POST.get('last_name').capitalize()
            temp.registration_upto = parser.parse(request.POST.get('registration_date')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
            
            # Handle fee status
            if request.POST.get('fee_status') == 'unpaid':
                temp.notification = 1
            
            # Save the trainer object
            model_save(temp)
            success = 'Successfully Added Trainer'

            # Add payments if payment is 'paid'
            if temp.fee_status == 'paid':
                payments = Payments(
                    user=temp,
                    payment_date=temp.registration_date,
                    payment_period=temp.subscription_period,
                    payment_amount=temp.amount
                )
                payments.save()

            # Fetch the last added Trainer
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
        result = 0
        if search_form.is_valid():
            first_name = request.POST.get('search')
            result = Trainer.objects.filter(first_name__contains=first_name)

        view_all = Trainer.objects.all()
        # get all trainers according to their batches
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
    print(id)
    Trainer.objects.filter(pk=id).delete()
    return redirect('view_trainer')

def update_trainer(request, id):
    if request.method == 'POST' and request.POST.get('export'):
        return export_all(Trainer.objects.filter(pk=id))
    if request.method == 'POST' and request.POST.get('no'):
        return redirect('/')
    if request.method == 'POST' and request.POST.get('gym_trainership'):
            gym_form = UpdateTrainerGymForm(request.POST)
            if gym_form.is_valid():
                object = Trainer.objects.get(pk=id)
                amount = request.POST.get('amount')
                day = (parser.parse(request.POST.get('registration_upto')) - delta.relativedelta(months=int(request.POST.get('subscription_period')))).day
                last_day = parser.parse(str(object.registration_upto)).day

                month = parser.parse(request.POST.get('registration_upto')).month
                last_month = parser.parse(str(object.registration_upto)).month
                # if status is stopped then do not update anything
                if object.stop == 1 and not request.POST.get('stop') == '0' and request.POST.get('gym_trainership'):
                    messages.error(request, 'Please start the status of user to update the record')
                    return redirect('update_trainer', id=object.pk)
                # to change only the batch
                elif (object.batch != request.POST.get('batch')):
                    object.batch = request.POST.get('batch')
                    object = check_status(request, object)
                    model_save(object)
                # check if user has modified only the date
                elif (datetime.datetime.strptime(str(object.registration_date), "%Y-%m-%d") != datetime.datetime.strptime(request.POST.get('registration_date'), "%Y-%m-%d")):
                        object.registration_date =  parser.parse(request.POST.get('registration_date'))
                        object.registration_upto =  parser.parse(request.POST.get('registration_date')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                        object.fee_status = request.POST.get('fee_status')
                        object = check_status(request, object)
                        model_save(object)
                # if amount and period are changed
                elif (object.amount != amount) and (object.subscription_period != request.POST.get('subscription_period')):
                    object.subscription_type =  request.POST.get('subscription_type')
                    object.subscription_period =  request.POST.get('subscription_period')
                    object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                    object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    object.fee_status = request.POST.get('fee_status')
                    object.amount =  request.POST.get('amount')
                    object = check_status(request, object)
                    model_save(object)
                # if only subscription_period is Changed
                elif (object.subscription_period != request.POST.get('subscription_period')):
                    object.subscription_period =  request.POST.get('subscription_period')
                    object = check_status(request, object)
                    model_save(object)
                # if amount and type are changed
                elif (object.amount != amount) and (object.subscription_type != request.POST.get('subscription_type')):
                    object.subscription_type =  request.POST.get('subscription_type')
                    object.subscription_period =  request.POST.get('subscription_period')
                    object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                    object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    object.fee_status = request.POST.get('fee_status')
                    object.amount =  request.POST.get('amount')
                    object = check_status(request, object)
                    model_save(object)
                # if amount ad fee status are changed
                elif (object.amount != amount) and ((request.POST.get('fee_status') == 'paid') or (request.POST.get('fee_status') == 'unpaid')):
                        object.amount = amount
                        object.fee_status = request.POST.get('fee_status')
                        object = check_status(request, object)
                        model_save(object)
                # if only amount is channged
                elif (object.amount != amount):
                    object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                    object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                    object.fee_status = request.POST.get('fee_status')
                    object.amount =  request.POST.get('amount')
                    if request.POST.get('fee_status') == 'unpaid':
                        object.notification =  1
                    elif request.POST.get('fee_status') == 'paid':
                        object.notification = 2
                    object = check_status(request, object)
                    model_save(object)
                # nothing is changed
                else:
                    if not request.POST.get('stop') == '1':
                        object.registration_date =  parser.parse(request.POST.get('registration_upto'))
                        object.registration_upto =  parser.parse(request.POST.get('registration_upto')) + delta.relativedelta(months=int(request.POST.get('subscription_period')))
                        object.amount =  request.POST.get('amount')
                        if request.POST.get('fee_status') == 'unpaid':
                            object.notification =  1
                        elif request.POST.get('fee_status') == 'paid':
                            object.notification = 2
                    object.fee_status = request.POST.get('fee_status')
                    object = check_status(request, object)
                    model_save(object)

                # Add payments if payment is 'paid'
                if object.fee_status == 'paid':
                    check = Payments.objects.filter(
                        payment_date=object.registration_date,
                        user__pk=object.pk).count()
                    if check == 0:
                        payments = Payments(
                                            user=object,
                                            payment_date=object.registration_date,
                                            payment_period=object.subscription_period,
                                            payment_amount=object.amount)
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
                    payments = Payments.objects.filter(user=user)
                except Payments.DoesNotExist:
                    payments = 'No Records'
                messages.success(request, 'Record updated successfully!')
                return redirect('update_trainer', id=user.pk)
            else:
                user = Trainer.objects.get(pk=id)
                info_form = UpdateTrainerInfoForm(initial={
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        'dob': user.dob,
                                        })

                try:
                    payments = Payments.objects.filter(user=user)
                except Payments.DoesNotExist:
                    payments = 'No Records'
                return render(request,
                    'update.html',
                    {
                        'payments': payments,
                        'gym_form': gym_form,
                        'info_form': info_form,
                        'user': user,
                        'subs_end_today_count': get_notification_count(),
                    })
    elif request.method == 'POST' and request.POST.get('info'):
        object = Trainer.objects.get(pk=id)
        object.first_name = request.POST.get('first_name')
        object.last_name = request.POST.get('last_name')
        object.dob = request.POST.get('dob')

        # for updating photo
        if 'photo' in request.FILES:
            myfile = request.FILES['photo']
            fs = FileSystemStorage(base_url="")
            photo = fs.save(myfile.name, myfile)
            object.photo = fs.url(photo)
        model_save(object)

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
            payments = Payments.objects.filter(user=user)
        except Payments.DoesNotExist:
            payments = 'No Records'

        return render(request,
            'update.html',
            {
                'payments': payments,
                'gym_form': gym_form,
                'info_form': info_form,
                'user': user,
                'updated': 'Record Updated Successfully',
                'subs_end_today_count': get_notification_count(),
            })
    else:
        user = Trainer.objects.get(pk=id)

        if len(Payments.objects.filter(user=user)) > 0:
            payments = Payments.objects.filter(user=user)
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
        return render(request,
                        'update.html',
                        {
                            'payments': payments,
                            'gym_form': gym_form,
                            'info_form': info_form,
                            'user': user,
                            'subs_end_today_count': get_notification_count(),
                        }
                    )


def attendance_view(request):
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


def edit_attendance(request, id):
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

def delete_attendance(request, record_id):
    record = get_object_or_404(TrainerAttendance, id=record_id)
    record.delete()
    return redirect('trainer_attendance')

def trainer(request):
    return render(request, 'trainer.html')