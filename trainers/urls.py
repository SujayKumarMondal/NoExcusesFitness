"""Trainers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views
from .views import attendance_view, edit_attendance
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('add/', login_required(views.add_trainer), name='add_trainer'),
    path('search/', login_required(views.search_trainer), name='search_trainer'),
    path('view/', login_required(views.view_trainer), name='view_trainer'),
    path('delete/<int:id>/', login_required(views.delete_trainer), name='delete_trainer'),
    path('update/<int:id>/', login_required(views.update_trainer), name='update_trainer'),
    path('attendance/', attendance_view, name='trainer_attendance'),
    path('', login_required(views.trainers), name='trainers'),
    path('attendance/edit/<int:id>/', views.edit_attendance, name='edit_trainer_attendance'),
    path('attendance/delete/<int:record_id>/', views.delete_attendance, name='delete_attendance'),
]
