from django.db import models
from members.models import Member
from trainers.models import Trainer
# Create your models here.
class TrainerPayments(models.Model):
    user = models.ForeignKey(Trainer, on_delete=models.CASCADE, null=True, blank=True)
    payment_date = models.DateField()
    payment_period = models.IntegerField()
    payment_amount = models.IntegerField()
