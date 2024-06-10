from __future__ import annotations

import threading

# django
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import *
from myproject import settings
import random, string
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@staticmethod
def generate_otp_and_send_email(email, user):
    otp = ''.join(random.choices(string.digits, k=6))
    subject = 'Your OTP for registration'
    from_email = settings.EMAIL_HOST_USER
    html_message = render_to_string('otp_emailer.html', {'otp': otp, 'user': user})
    plain_message = strip_tags(html_message)

    def send_mail_thread():
        send_mail(
            subject,
            plain_message,
            from_email,
            [email],
            html_message=html_message,
            fail_silently=True
        )
    mail_thread = threading.Thread(target=send_mail_thread)
    mail_thread.start()
    EmailOtp.objects.create(
        email=email,
        otp=otp
    )
    return otp

@staticmethod
def generate_otp_forget(email, user):
    otp = ''.join(random.choices(string.digits, k=6))
    subject = 'Your OTP for Forget Password'
    from_email = settings.EMAIL_HOST_USER
    html_message = render_to_string('otp_forget.html', {'otp': otp, 'user': user})
    plain_message = strip_tags(html_message)

    def send_mail_thread():
        send_mail(
            subject,
            plain_message,
            from_email,
            [email],
            html_message=html_message,
            fail_silently=True
        )
    mail_thread = threading.Thread(target=send_mail_thread)
    mail_thread.start()
    EmailOtp.objects.create(
        email=email,
        otp=otp
    )
    return otp

