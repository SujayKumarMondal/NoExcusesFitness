from django.db import models
from members.models import Member
from trainers.models import Trainer
# Create your models here.
class Payments(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    # trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    payment_date = models.DateField()
    payment_period = models.IntegerField()
    payment_amount = models.IntegerField()
