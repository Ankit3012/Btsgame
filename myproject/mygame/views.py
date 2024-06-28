from rest_framework.generics import *
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import *
from .helpers import *
import random, string
from decimal import Decimal
import logging
from .models import *
from time import sleep
from django.contrib.auth.hashers import make_password

logger = logging.getLogger('myapp')


# Create your views here.
class RegisterUser(APIView):

    def generate_username(self):
        length = 10  # You can adjust the length of the username as needed
        while True:
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
            if not UserProfile.objects.filter(username=username).exists():
                return username

    def generate_refer_code(self, fullname):
        length = 10  # You can adjust the length of the username as needed
        while True:
            refer_code = ''.join(random.choices(fullname + string.ascii_lowercase + string.digits, k=length))
            if not UserProfile.objects.filter(refer_code=refer_code).exists():
                return refer_code

    def post(self, request):
        try:
            data = request.data
            phone = data.get('phone')
            email = data.get('email')
            parent_refer_code = data.get('refer_code', 'BTS786')
            fullname = data.get('fullname')
            profile_pic = request.FILES.get('image', 'unknown_user.png')

            username = self.generate_username()
            refer_code = self.generate_refer_code(fullname)
            email = str(email).lower()
            user_phone = UserProfile.objects.filter(phone=phone).first()

            if user_phone:
                # If user is active, return user already exists
                return Response({'error': True, 'status': False, 'message': "User already exists!"},
                                status=status.HTTP_200_OK)

            # Check if user with email exists
            user_email = UserProfile.objects.filter(email=email).first()

            if user_email:
                return Response({'error': True, 'status': False, 'message': "User already exists!"},
                                status=status.HTTP_200_OK)
            otp = generate_otp_and_send_email(email, data.get('fullname'))
            if not otp:
                return Response({'status': False, 'message': 'OTP not sent'}, status=status.HTTP_400_BAD_REQUEST)
            user = UserProfile.objects.create(
                full_name=fullname,
                phone=phone,
                username=username,  # Assuming 'phone' is the username
                email=email,
                is_active=False,
                profile_pic=profile_pic,
                refer_code=refer_code,
                parent_referral=parent_refer_code,
            )
            user.set_password(data.get('password'))
            user.save()

            serializer = UserRegisterSerializer(user)

            return Response({'success': True, 'data': serializer.data, 'message': "Successfully Registered!"},
                            status=status.HTTP_201_CREATED)

        except KeyError as e:
            raise ValidationError(f"Missing required field: {e}")

        except ValidationError as e:
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': False, 'message': "An error occurred while processing your request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOtp(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'status': False, 'message': 'Email and OTP are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Fetch the latest OTP for the given email
        otp_obj = EmailOtp.objects.filter(email=email).last()

        if not otp_obj:
            return Response({'status': False, 'message': 'OTP not sent'}, status=status.HTTP_400_BAD_REQUEST)

        if int(otp) != int(otp_obj.otp):
            return Response({'status': False, 'message': 'Wrong OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is correct, activate the user and delete the OTP record
        user = UserProfile.objects.filter(email=email).first()
        if not user:
            return Response({'status': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()

        otp_obj.delete()

        return Response({'status': True, 'message': 'User Successfully Registered'}, status=status.HTTP_200_OK)


class ForgetPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('password')
        user = UserProfile.objects.get(email=email)
        #
        otp_obj = EmailOtp.objects.filter(email=email).last()

        if not otp_obj:
            return Response({'status': False, 'message': 'OTP Not sent'}, status=status.HTTP_400_BAD_REQUEST)

        if int(otp) != int(otp_obj.otp):
            return Response({'status': False, 'message': 'Wrong OTP'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            otp_obj = EmailOtp.objects.filter(email=email).last()

            # Update the password
            user.password = make_password(new_password)
            user.save()

            # Delete the OTP object
            otp_obj.delete()

            return Response({'status': True, 'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


class LoginUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            if '@' in email:
                user = UserProfile.objects.get(email=email)

            else:
                user = UserProfile.objects.get(phone=email)

            if not user.check_password(password):
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if user.is_active:
                    tokens = self.get_tokens_for_user(user)
                    return Response(
                        {'refresh': tokens['refresh'], 'message': 'Login successful'},
                        status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User is inactive'}, status=status.HTTP_401_UNAUTHORIZED)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# Admin Login

class AdminLoginUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            if '@' in email:
                user = AdminProfile.objects.get(email=email)

            else:
                user = AdminProfile.objects.get(phone=email)
            db_password = user.password

            if str(password) != str(db_password):
                return Response({'error': 'Invalid Admin email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if user.is_active:
                    tokens = self.get_tokens_for_user(user)
                    return Response(
                        {'refresh': tokens['refresh'], 'message': 'Admin Login successful'},
                        status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Admin is inactive'}, status=status.HTTP_401_UNAUTHORIZED)

        except UserProfile.DoesNotExist:
            return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
        }


class LotteryCreate(APIView):

    def get(self, request):
        lottery = Lottery.objects.filter(is_active=True).first()
        if not lottery:
            return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LotterySerializer(lottery)
        return Response(serializer.data)

    def post(self, request):
        try:
            lottery = Lottery.objects.filter(is_active=True).first()
            if lottery:
                time_remaining = (lottery.end_time - timezone.now()).total_seconds()
                if time_remaining > 0:
                    return Response({'time_remaining': time_remaining, 'message': 'Lottery still running'},
                                    status=status.HTTP_200_OK)
            else:
                Lottery.objects.all().delete()
                game_time = GameDetails.objects.get(game_name='lottery')
                Lottery.objects.create(
                    start_time=timezone.now(),
                    end_time=timezone.now() + timezone.timedelta(minutes=int(game_time.lottery_time))
                )
                sleep(180)  # Delay for 3 minutes
                lottery = Lottery.objects.filter(is_active=True).first()
                if not lottery:
                    return Response({'error': 'Failed to create a new lottery.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                winning_number = random.randint(1, 9)
                winning_tickets = LotteryTicket.objects.filter(lottery=lottery, number=winning_number)
                print(winning_tickets)

                if winning_tickets.exists():
                    total_prize = Decimal(lottery.total_revenue) * Decimal(float(game_time.user_revenue))
                    print('game_time.user_revenue:', game_time.user_revenue)
                    admin = AdminProfile.objects.filter(is_superuser=True).first()
                    company_commission = Decimal(lottery.total_revenue) * Decimal(float(game_time.comp_revenue))
                    print('game_time.comp_revenue:', game_time.comp_revenue)
                    admin.main_wallet += company_commission
                    admin.save()

                    prize_per_ticket = total_prize / winning_tickets.count()

                    for ticket in winning_tickets:
                        user = ticket.user
                        user.main_wallet += prize_per_ticket
                        user.save()

                        # Create a transaction record for the winning user
                        Transaction.objects.create(
                            user=user,
                            lottery=lottery,
                            lottery_code=lottery.lottery_code,
                            balance=user.main_wallet,
                            revenue=lottery.total_revenue,
                            credit=prize_per_ticket,
                            description=f"No. {winning_number} Lottery wins - Your Ticket id is {ticket.id}"
                        )

                else:
                    admin = AdminProfile.objects.filter(is_superuser=True).first()
                    company_commission = lottery.total_revenue
                    admin.main_wallet += company_commission
                    admin.save()

                AdminTransaction.objects.create(
                    user=admin,
                    game_name='Lottery',
                    game_code=lottery.lottery_code,
                    balance=admin.main_wallet,
                    revenue=lottery.total_revenue,
                    credit=company_commission,
                    description=f"Rs. {company_commission} has been credited from {lottery.lottery_code} this lottery."
                )

                LotteryHistory.objects.create(
                    lottery_code=lottery.lottery_code,
                    total_bet=lottery.total_revenue,
                    result=winning_number
                )

                print(lottery.lottery_code)

                lottery.delete()
                return Response({'message': f'Lottery Ended and Result is {winning_number}'},
                                status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class LotteryCreate(APIView):
#
#     def get(self, request):
#         lottery = Lottery.objects.filter(is_active=True).first()
#         if not lottery:
#             return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = LotterySerializer(lottery)
#         return Response(serializer.data)
#
#     def post(self, request):
#         try:
#             lottery = Lottery.objects.filter(is_active=True).first()
#             if lottery:
#                 time_remaining = (lottery.end_time - timezone.now()).total_seconds()
#                 if time_remaining > 0:
#                     return Response({'time_remaining': time_remaining, 'message': 'Lottery still running'},
#                                     status=status.HTTP_200_OK)
#             elif not lottery:
#                 Lottery.objects.all().delete()
#                 game_time = GameDetails.objects.get(game_name='lottery')
#                 Lottery.objects.create(
#                     start_time=timezone.now(),
#                     end_time=timezone.now() + timezone.timedelta(minutes=int(game_time.lottery_time))
#                 )
#                 sleep(180)  # Delay for 3 minutes
#                 lottery = Lottery.objects.filter(is_active=True).first()
#                 winning_number = random.randint(1, 9)
#                 winning_tickets = LotteryTicket.objects.filter(lottery=lottery, number=winning_number)
#                 print(winning_tickets)
#
#                 if winning_tickets.exists():
#                     total_prize = Decimal(lottery.total_revenue) * Decimal(float(game_time.user_revenue))
#                     print('game_time.user_revenue:', game_time.user_revenue)
#                     admin = AdminProfile.objects.filter(is_superuser=True).first()
#                     company_commission = Decimal(lottery.total_revenue) * Decimal(float(game_time.comp_revenue))
#                     print('game_time.comp_revenue:', game_time.comp_revenue)
#                     admin.main_wallet += company_commission
#                     admin.save()
#
#                     prize_per_ticket = total_prize / winning_tickets.count()
#
#                     for ticket in winning_tickets:
#                         user = ticket.user
#                         user.main_wallet += prize_per_ticket
#                         user.save()
#
#                         # Create a transaction record for the winning user
#                         Transaction.objects.create(
#                             user=user,
#                             lottery=lottery,
#                             lottery_code=lottery.lottery_code,
#                             balance=user.main_wallet,
#                             revenue=lottery.total_revenue,
#                             credit=prize_per_ticket,
#                             description=f"No. {winning_number} Lottery wins - Your Ticket id is {ticket.id}"
#                         )
#
#                 else:
#                     admin = AdminProfile.objects.filter(is_superuser=True).first()
#                     company_commission = lottery.total_revenue
#                     admin.main_wallet += company_commission
#                     admin.save()
#
#                 AdminTransaction.objects.create(
#                     user=admin,
#                     game_name='Lottery',
#                     game_code=lottery.lottery_code,
#                     balance=admin.main_wallet,
#                     revenue=lottery.total_revenue,
#                     credit=company_commission,
#                     description=f"Rs. {company_commission} has been credited from {lottery.lottery_code} this lottery."
#                 )
#
#                 LotteryHistory.objects.create(
#
#                     lottery_code=lottery.lottery_code,
#                     total_bet=lottery.total_revenue,
#                     result=winning_number
#                 )
#
#                 print(lottery.lottery_code)
#
#                 lottery.delete()
#                 return Response({'message': f'Lottery Ended and Result is {winning_number}'},
#                                 status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'error': 'No lottery found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LotteryAPI(APIView):
    def get(self, request):
        lottery = Lottery.objects.filter(is_active=True).first()
        if not lottery:
            return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LotterySerializer(lottery)
        return Response(serializer.data)

    def post(self, request):
        lottery = Lottery.objects.filter(is_active=True).first()
        if not lottery:
            return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)

        if lottery.tickets_remaining == 0:
            return Response({'error': 'All tickets for this lottery have been sold'},
                            status=status.HTTP_400_BAD_REQUEST)

        numbers = request.data.get('number')
        if not numbers:
            return Response({'error': 'No numbers provided'}, status=status.HTTP_400_BAD_REQUEST)

        for number in numbers.split(','):
            if int(number) < 1 or int(number) > 9:
                return Response({'error': 'Invalid lottery number'}, status=status.HTTP_400_BAD_REQUEST)

        user = UserProfile.objects.get(id=request.data.get('user'))
        total_tickets = len(numbers.split(','))
        total_cost = total_tickets * 10  # Assuming the ticket price is 10 per ticket

        if user.main_wallet < total_cost:
            return Response({'error': 'Insufficient balance in main wallet'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.main_wallet -= total_cost
        user.save()
        Transaction.objects.create(
            user=user,
            lottery=lottery,
            lottery_code=lottery.lottery_code,
            balance=user.main_wallet,
            revenue=lottery.total_revenue,
            debit=total_cost,
            description=f"Purchased lottery Ticket, Lottery id: {lottery.lottery_code}"
        )
        # if user.main_wallet <10
        for number in numbers.split(','):
            ticket = LotteryTicket.objects.create(
                user=user,
                lottery=lottery,
                number=number
            )
            lottery.tickets_remaining -= 1
            lottery.total_revenue += 10
            lottery.save()

        return Response({'message': 'Lottery tickets purchased successfully'}, status=status.HTTP_201_CREATED)


class LotteryTimerAPI(APIView):
    def get(self, request):
        print(type(0.9))
        lottery = Lottery.objects.filter(is_active=True).first()
        if not lottery:
            return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)

        time_remaining = (lottery.end_time - timezone.now()).total_seconds()
        if time_remaining <= 0:
            return Response({'message': 'Lottery has ended'}, status=status.HTTP_200_OK)

        return Response({'time_remaining': time_remaining}, status=status.HTTP_200_OK)


# class LotteryResultAPI(APIView):
#     def get(self, request):
#         all = LotteryTicket.objects.all()
#         serializer = LotteryTransactionSerializer(all, many=True)
#         return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class LotteryTransaction(APIView):
    def get(self, request):
        all = LotteryTicket.objects.all()
        serializer = LotteryTransactionSerializer(all, many=True)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class Profile(APIView):
    def get(self, request):
        user_id = self.request.query_params.get('user')
        user_transaction = self.request.query_params.get('transaction')
        if user_id:

            if user_transaction == 'true':
                all = Transaction.objects.filter(user_id=user_id)
                serializer = TransactionSerializer(all, many=True)
                return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)

            user = UserProfile.objects.get(id=user_id)
            serializer = ProfileSerializer(user)
            return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            user = UserProfile.objects.all()
            serializer = ProfileSerializer(user, many=True)
            return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class AdminProfileList(APIView):
    def get(self, request):
        admin_profiles = AdminProfile.objects.all()
        serializer = AdminProfileSerializer(admin_profiles, many=True)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class SupportViewSet(APIView):
    def get(self, request):
        report = Support.objects.filter(resolve=False, is_active=True)
        serializer = SupportSerializer(report, many=True)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SupportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data.pop('user')
            support = Support.objects.create(**serializer.validated_data, user=user)
            return Response({'status': True}, status=status.HTTP_201_CREATED)
        return Response({'status': False}, status=status.HTTP_400_BAD_REQUEST)


class LotteryHistoryViewSet(APIView):
    def get(self, request):
        result = self.request.query_params.get('result')
        if result == 'last':
            num = LotteryHistory.objects.last().result
            return Response({'status': True, 'data': num}, status=status.HTTP_200_OK)

        report = LotteryHistory.objects.all().order_by('-id')
        serializer = LotteryHistorySerializer(report, many=True)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)
