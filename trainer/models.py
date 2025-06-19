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



class TrainerAttendance(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, default=1)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.trainer.first_name} {self.trainer.last_name} - {self.date} - {self.status}"