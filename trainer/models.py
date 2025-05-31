from django.db import models

class Trainer(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    reg_date = models.DateField()
    reg_upto = models.DateField()
    sub_type = models.CharField(max_length=100)
    sub_period = models.PositiveIntegerField()
    fees_amount = models.DecimalField(max_digits=8, decimal_places=2)
    fees_status = models.CharField(max_length=10)

    def __str__(self):
        return self.name
