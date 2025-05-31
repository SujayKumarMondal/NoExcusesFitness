from django.urls import path
from . import views

urlpatterns = [
    path('', views.trainer_view, name='trainer'),  # List and add
    path('edit/<int:trainer_id>/', views.edit_trainer, name='edit_trainer'),
    path('delete/<int:trainer_id>/', views.delete_trainer, name='delete_trainer'),
]
