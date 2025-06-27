from django.shortcuts import render, redirect, get_object_or_404
from members.models import Member
from trainers.models import Trainer
from .config import get_notification_count, run_notifier, my_handler
from django.db.models import Q
from django.db.models.signals import post_save
import datetime

def notifications(request):
    now = datetime.datetime.now()
    two_days_later = datetime.date.today() + datetime.timedelta(days=2)

    # Members
    morning_members_before = Member.objects.filter(
        Q(registration_upto__lte=now, notification=1, batch='morning') |
        Q(fee_status='pending', notification=1, batch='morning')
    ).exclude(stop=1).order_by('first_name')

    morning_members_today = Member.objects.filter(
        registration_upto__gte=now,
        registration_upto__lte=two_days_later,
        notification=1, batch='morning'
    ).exclude(stop=1).order_by('first_name')

    evening_members_before = Member.objects.filter(
        Q(registration_upto__lte=now, notification=1, batch='evening') |
        Q(fee_status='pending', notification=1, batch='evening')
    ).exclude(stop=1).order_by('first_name')

    evening_members_today = Member.objects.filter(
        registration_upto__gte=now,
        registration_upto__lte=two_days_later,
        notification=1, batch='evening'
    ).exclude(stop=1).order_by('first_name')

    # Trainers
    morning_trainers_before = Trainer.objects.filter(
        Q(registration_upto__lte=now, notification=1, batch='morning') |
        Q(fee_status='unpaid', notification=1, batch='morning')
    ).exclude(stop=1).order_by('first_name')

    morning_trainers_today = Trainer.objects.filter(
        registration_upto__gte=now,
        registration_upto__lte=two_days_later,
        notification=1, batch='morning'
    ).exclude(stop=1).order_by('first_name')

    evening_trainers_before = Trainer.objects.filter(
        Q(registration_upto__lte=now, notification=1, batch='evening') |
        Q(fee_status='unpaid', notification=1, batch='evening')
    ).exclude(stop=1).order_by('first_name')

    evening_trainers_today = Trainer.objects.filter(
        registration_upto__gte=now,
        registration_upto__lte=two_days_later,
        notification=1, batch='evening'
    ).exclude(stop=1).order_by('first_name')

    context = {
        'subs_end_today_count': get_notification_count(),
        'morning_members_today': morning_members_today,
        'morning_trainers_today': morning_trainers_today,
        'morning_members_before': morning_members_before,
        'morning_trainers_before': morning_trainers_before,
        'evening_members_today': evening_members_today,
        'evening_trainers_today': evening_trainers_today,
        'evening_members_before': evening_members_before,
        'evening_trainers_before': evening_trainers_before,
    }
    return render(request, 'notifications.html', context)


def notification_delete(request, id):
    try:
        member = Member.objects.get(pk=id)
        post_save.disconnect(my_handler, sender=Member)
        member.notification = 0
        member.stop = 1
        member.save()
        post_save.connect(my_handler, sender=Member)
    except Member.DoesNotExist:
        try:
            trainer = Trainer.objects.get(pk=id)
            post_save.disconnect(my_handler, sender=Trainer)
            trainer.notification = 0
            trainer.stop = 1
            trainer.save()
            post_save.connect(my_handler, sender=Trainer)
        except Trainer.DoesNotExist:
            pass  # Or handle error

    return redirect('/notifications/')
