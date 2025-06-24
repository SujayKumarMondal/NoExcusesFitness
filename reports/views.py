from django.shortcuts import render, redirect
from django.http import HttpResponse
from members.models import Member
import csv
import datetime
from .models import GenerateReportForm
from django.db.models import Q
from notifications.config import get_notification_count

# Create your views here.
def export_all(user_obj):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['First name', 'Last name', 'DOB', 'Mobile', 'Admission Date', 'Subscription Type', 'Batch'])
    members = user_obj.values_list('first_name', 'last_name', 'dob', 'mobile_number', 'admitted_on', 'subscription_type', 'batch')
    for user in members:
        writer.writerow(user)

    return response

def reports(request):
    if request.method == 'POST':
        form = GenerateReportForm(request.POST)
        if form.is_valid():
            month = request.POST.get('month')
            year = request.POST.get('year')
            batch = request.POST.get('batch')

            # Convert to integers if not empty
            month = int(month) if month else None
            year = int(year) if year else None

            filters = {}
            if month:
                filters['registration_date__month'] = month
            if year:
                filters['registration_date__year'] = year
            if batch and batch != 'All':
                filters['batch'] = batch

            if 'generate_all' in request.POST or 'export' in request.POST:
                # Always filter based on selected fields
                users = Member.objects.filter(**filters) if filters else Member.objects.all()
            else:
                users = Member.objects.filter(**filters) if filters else Member.objects.none()
            
            if 'export' in request.POST:
                return export_all(users)
            
            context = {
                'users': users,
                'form': form,
                'subs_end_today_count': get_notification_count(),
            }
            return render(request, 'reports.html', context)
    else:
        form = GenerateReportForm()
    return render(request, 'reports.html', {'form': form, 'subs_end_today_count': get_notification_count(),})