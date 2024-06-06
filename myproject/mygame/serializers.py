from rest_framework import serializers
from .models import *

from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'full_name', 'phone', 'password', 'email', 'profile_pic', 'is_verified', 'is_active')


class LotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lottery
        fields = ['id', 'start_time', 'end_time', 'is_active', 'total_revenue', 'tickets_remaining', 'lottery_code']
        read_only_fields = ['id', 'lottery_code']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = '__all__'


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ['id', 'user', 'description', 'image', 'resolve', 'is_active']
        read_only_fields = ['resolve', 'is_active']

    def create(self, validated_data):
        user = self.context['request'].user
        print(validated_data)
        support = Support.objects.create(user=user, **validated_data)
        return support


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class LotteryTransactionSerializer(serializers.ModelSerializer):
    lottery_code = serializers.CharField(source='lottery.lottery_code')

    class Meta:
        model = LotteryTicket
        fields = ['user', 'lottery', 'number', 'created_at', 'lottery_code']
