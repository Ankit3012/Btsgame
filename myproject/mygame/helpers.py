from __future__ import annotations

import threading

# django
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import *
from myproject import settings
import random, string


def generate_otp_and_send_email(email):
    otp = ''.join(random.choices(string.digits, k=6))
    subject = 'Your OTP for registration'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER

    def send_mail_thread():
        print('success1')
        send_mail(subject, message, from_email, [email])
        print('success2')
        EmailOtp.objects.create(email=email, otp=otp)

    mail_thread = threading.Thread(target=send_mail_thread)
    mail_thread.start()
    print(otp)

    return otp
