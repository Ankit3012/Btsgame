from django.urls import path,include
from .views import *
urlpatterns = [
    path('register/',RegisterUser.as_view(),name='register'),
    path('login/',LoginUser.as_view(),name='login'),
    path('verify/otp/',VerifyOtp.as_view(),name='verify-otp'),
    path('lottery_create/',LotteryCreate.as_view(),name='lottery-create'),
    path('ticket_create/',LotteryAPI.as_view(),name='ticket-create'),
    path('lottery_timer/',LotteryTimerAPI.as_view(),name='lottery-timer'),
    path('lottery_history/',LotteryHistoryViewSet.as_view(),name='lottery_history'),
    # path('lottery_result/',LotteryResultAPI.as_view(),name='lottery-result'),
    path('profile/',Profile.as_view(),name='profile'),
    path('lottery_user_history/',LotteryTransaction.as_view(),name='lottery_user_history'),
    path('support/',SupportViewSet.as_view(),name='support'),

    # Admin
    path('admin_login/',AdminLoginUser.as_view(),name='admin_login'),
    path('admin_profile/',AdminProfileList.as_view(),name='admin_profile'),


]
