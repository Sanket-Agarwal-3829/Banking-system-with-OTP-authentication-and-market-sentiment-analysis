import random
from django.core.mail import send_mail
from django.conf import settings
from django_otp.models import Device
from django.db import models 

class EmailDevice(Device):
    otp = models.CharField(max_length=6, blank=True, null=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        return self.otp

    def verify_otp(self, otp):
        return self.otp == otp

def send_otp_via_email(user):
    device, created = EmailDevice.objects.get_or_create(user=user, name='email')
    otp = device.generate_otp()
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)
