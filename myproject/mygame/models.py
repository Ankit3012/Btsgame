from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
# from .choices import Flag
from django.conf import settings
import uuid
from django.urls import reverse


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EmailOtp(models.Model):
    email = models.CharField(max_length=200)
    otp = models.CharField(max_length=9, null=True, blank=True)
    otpcount = models.IntegerField(default=0)
    validated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.email) + 'is sent' + (str(self.otp))


class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, password, phone, pin=None, **extra_fields):
        if not username:
            raise ValueError("User must have username!")
        if not email:
            raise ValueError("User must have email!")

        user = self.model(email=self.normalize_email(email), username=username, phone=phone,
                          pin=pin, password=password, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, phone, **extra_fields):

        user = self.create_user(email=self.normalize_email(email), username=username, password=password, phone=phone,
                                **extra_fields)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=200, unique=True, null=True, blank=True)
    username = models.CharField(max_length=500, unique=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)

    # All these field are required for custom user model
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # other
    full_name = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    pin = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_pic = models.ImageField(default="media/unknown_user.png", blank=True, null=True, upload_to='Profile_Pics')
    refer_code = models.UUIDField(unique=True, auto_created=True, default=uuid.uuid4, editable=False)
    parent_referral = models.CharField(max_length=1000, blank=True, null=True)
    pool = models.IntegerField(blank=True, null=True, default=0)
    device_token = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    main_wallet = models.DecimalField(max_digits=12, decimal_places=3, null=False, blank=False, default=0)
    referral_wallet = models.DecimalField(max_digits=12, decimal_places=3, null=False, blank=False, default=0)
    terms_privacy = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    def save(self, *args, **kwargs):
        if not self.id:  # Check if the object is being created for the first time
            last_user = UserProfile.objects.last()
            if last_user:
                self.id = last_user.id + 1
            else:
                self.id = 1
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        try:
            return f'{str(self.id)}  |  {self.full_name} '
        except:
            return "_"

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def user_roles(self):
        return " | ".join([str(ur) for ur in self.user_role.all()])

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class AdminProfile(models.Model):
    email = models.EmailField(verbose_name="admin_email", max_length=200, unique=True, null=True, blank=True)
    username = models.CharField(max_length=500, unique=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, unique=True)
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now=True)

    # All these field are required for custom user model
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # other
    full_name = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    pin = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_pic = models.ImageField(default="media/unknown_user.png", blank=True, null=True, upload_to='Profile_Pics')
    refer_code = models.UUIDField(unique=True, auto_created=True, default=uuid.uuid4, editable=False)
    parent_referral = models.CharField(max_length=1000, blank=True, null=True)
    device_token = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    main_wallet = models.DecimalField(max_digits=12, decimal_places=3, null=False, blank=False, default=0)
    referral_wallet = models.DecimalField(max_digits=12, decimal_places=3, null=False, blank=False, default=0)
    terms_privacy = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:  # Check if the object is being created for the first time
            last_user = AdminProfile.objects.last()
            if last_user:
                self.id = last_user.id + 1
            else:
                self.id = 1
        super(AdminProfile, self).save(*args, **kwargs)

    def __str__(self):
        try:
            return f'{str(self.id)}  |  {self.full_name} '
        except:
            return "_"


class Lottery(models.Model):
    lottery_code = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    lottery_time = models.CharField(max_length=200, null=False, blank=False, default=3)
    lottery_price = models.CharField(max_length=200, null=False, blank=False, default=10)
    is_active = models.BooleanField(default=True)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tickets_remaining = models.IntegerField(default=100)

    def __str__(self):
        return f"Lottery ({self.start_time} - {self.end_time})"


class GameDetails(Base):
    game_name = models.CharField(max_length=200, null=False, blank=False, default='lottery')
    lottery_time = models.CharField(max_length=200, null=False, blank=False, default=3)
    lottery_price = models.CharField(max_length=200, null=False, blank=False, default=10)
    comp_revenue = models.CharField(max_length=200, null=False, blank=False, default=10)
    user_revenue = models.CharField(max_length=200, null=False, blank=False, default=90)
    referal_per = models.CharField(max_length=200, null=False, blank=False, default=10)

    def __str__(self):
        return f"Lottery ({self.lottery_time} - {self.lottery_price})"


class Support(Base):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_support')
    description = models.CharField(max_length=2000, null=True, blank=True)
    image = models.ImageField(blank=True, null=True)
    resolve = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Support Ticket user {self.user.full_name}"


class LotteryTicket(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='lottery_tickets')
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, related_name='tickets')
    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} - Lottery {self.lottery.id}"


class Transaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_transaction')
    lottery = models.ForeignKey(Lottery, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='transaction_lottery')
    lottery_code = models.CharField(max_length=2000, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    debit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - User: {self.user.username}"


class AdminTransaction(Base):
    user = models.ForeignKey(AdminProfile, on_delete=models.CASCADE, related_name='admin_transaction')
    game_name = models.CharField(max_length=2000, blank=True, null=True)
    game_code = models.CharField(max_length=2000, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    debit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin Transaction {self.id} - User: {self.user.username} - game: {self.game_name}"

    class LotteryHistory(Base):
        user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='lottery_history')
        lottery_code = models.CharField(max_length=2000, blank=True, null=True)

        balance = models.DecimalField(max_digits=12, decimal_places=2)
        revenue = models.DecimalField(max_digits=12, decimal_places=2)
        debit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
        credit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
        description = models.CharField(max_length=255)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"Transaction {self.id} - User: {self.user.username}"
