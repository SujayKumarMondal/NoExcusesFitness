from django.test import TestCase
from .models import Member
import datetime

# Create your tests here.
class MemberTestCase(TestCase):
    def setUp(self):
        Member.objects.create(
                                first_name='Sujay',
                                last_name='Mondal',
                                mobile_number='4616461451',
                                email='sujay@gmail.com',
                                registration_date=datetime.datetime.now(),
                                subscription_type='gym',
                                subscription_period='1',
                                amount='500',
                                fee_status='paid',
                                batch='morning',
                            )

    def test_member(self):
        check = Member.objects.get(first_name='Sujay')
        print(check)
