from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(AdminProfile)
admin.site.register(EmailOtp)
admin.site.register(Lottery)
admin.site.register(LotteryTicket)
admin.site.register(Transaction)