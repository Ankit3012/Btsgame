from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(AdminProfile)
admin.site.register(Support)
admin.site.register(EmailOtp)
admin.site.register(GameDetails)
admin.site.register(LotteryHistory)
admin.site.register(Lottery)
admin.site.register(LotteryTicket)
admin.site.register(Transaction)
admin.site.register(AdminTransaction)