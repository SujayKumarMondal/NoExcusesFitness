from django.test import TestCase
from .models import Trainer
import datetime

# Create your tests here.
class TrainerTestCase(TestCase):
    def setUp(self):
        Trainer.objects.create(
                                first_name='Sujay',
                                last_name='Mondal',
                                mobile_number='6461567890',
                                mobile_number='4616461451',
                                email='sujay@gmail.com',
                                registration_date=datetime.datetime.now(),
                                subscription_type='gym',
                                subscription_period='1',
                                amount='500',
                                fee_status='paid',
                                batch='morning',
                            )

    def test_trainer(self):
        check = Trainer.objects.get(first_name='Sujay')
        print(check)
