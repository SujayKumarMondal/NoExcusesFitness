from django.urls import path
from . import views
from .views import trainer_attendance_view, edit_trainer_attendance, delete_trainer_attendance
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.trainer_view, name='trainer'),  # List and add
    path('edit/<int:trainer_id>/', views.edit_trainer, name='edit_trainer'),
    path('delete/<int:trainer_id>/', views.delete_trainer, name='delete_trainer'),
    path('attendance/', trainer_attendance_view, name='trainer_attendance'),
    path('editAttendance/edit/<int:id>/', edit_trainer_attendance, name='edit_trainer_attendance'),
    path('deleteAttendance/delete/<int:record_id>/', views.delete_trainer_attendance, name='delete_trainer_attendance'),
]
