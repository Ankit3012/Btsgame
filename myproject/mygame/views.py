from rest_framework.generics import *
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import *
from .helpers import *
import random, string
from decimal import Decimal
import logging
logger = logging.getLogger('myapp')

# Create your views here.
class RegisterUser(APIView):

    def generate_username(self):
        length = 10  # You can adjust the length of the username as needed
        while True:
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
            if not UserProfile.objects.filter(username=username).exists():
                return username

    def post(self, request):
        try:
            data = request.data
            phone = data.get('phone')
            email = data.get('email')
            otp = data.get('otp')
            fullname = data.get('fullname')
            profile_pic = request.FILES.get('image', None)

            username = self.generate_username()
            email = str(email).lower()
            user_phone = UserProfile.objects.filter(phone=phone).first()
            # print(user_phone)

            if user_phone:
                # If user is active, return user already exists
                return Response({'error': True, 'status': False, 'message': "User already exists!"},
                                status=status.HTTP_200_OK)

            # Check if user with email exists
            user_email = UserProfile.objects.filter(email=email).first()

            if user_email:
                return Response({'error': True, 'status': False, 'message': "User already exists!"},
                                status=status.HTTP_200_OK)
            # generate_otp_and_send_email(email=email)
            print('an')
            logger.info('Successfully added likes to posts')

            otp_obj = EmailOtp.objects.filter(email=email).last()

            if not otp_obj:
                return Response({'status': False, 'message': 'OTP '}, status=status.HTTP_400_BAD_REQUEST)
            print(otp_obj)
            if int(otp) != int(otp_obj.otp):
                return Response({'status': False, 'message': 'Wrong OTP'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                otp_obj = EmailOtp.objects.filter(email=email).last()

                otp_obj.delete()
                # Create new user profile
                user = UserProfile.objects.create(
                    full_name=fullname,
                    phone=phone,
                    username=username,  # Assuming 'phone' is the username
                    email=email,
                    is_active=True,
                    profile_pic=profile_pic
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

        try:

            logger.info('success enter otp')
            generate_otp_and_send_email(email=email)
            logger.info('success otp')
            return Response({'status': True, 'message': 'OTP Sent'}, status=status.HTTP_200_OK)
        except EmailOtp.DoesNotExist:
            return Response({'status': False, 'message': 'OTP not found'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'status': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': False, 'message': 'An error occurred while verifying OTP'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUser(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = UserProfile.objects.get(email=email)
            if not user.check_password(password):
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                if user.is_active:
                    tokens = self.get_tokens_for_user(user)
                    return Response(
                        {'refresh': tokens['refresh'], 'access': tokens['access'], 'message': 'Login successful'},
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


# class LoginUser(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         user = UserProfile.objects.get(email=email)
#
#         def getTokensForUser(user):
#             refresh = RefreshToken.for_user(user)
#             return {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#
#         tokens = getTokensForUser(user)
#         return Response({'refresh': str(tokens.get('refresh')), 'access': str(tokens.get('access')),
#                          "Success": "Login successfully"}, status=status.HTTP_200_OK)


class LotteryCreate(APIView):
    def post(self, request):
        Lottery.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(minutes=2)
        )
        return Response({'message': 'Lottery Created successfully'}, status=status.HTTP_201_CREATED)


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
        lottery = Lottery.objects.filter(is_active=True).first()
        if not lottery:
            return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)

        time_remaining = (lottery.end_time - timezone.now()).total_seconds()
        if time_remaining <= 0:
            return Response({'message': 'Lottery has ended'}, status=status.HTTP_200_OK)

        return Response({'time_remaining': time_remaining}, status=status.HTTP_200_OK)


class LotteryResultAPI(APIView):

    def post(self, request):
        lottery = Lottery.objects.filter(is_active=True).first()
        if not lottery:
            return Response({'error': 'No active lottery found'}, status=status.HTTP_404_NOT_FOUND)

        if lottery.end_time > timezone.now():
            return Response({'error': 'Lottery is still active'}, status=status.HTTP_400_BAD_REQUEST)

        winning_number = request.data.get('winning_number')
        if not winning_number:
            winning_number = random.randint(1, 9)

        if int(winning_number) < 1 or int(winning_number) > 9:
            return Response({'error': 'Invalid winning number'}, status=status.HTTP_400_BAD_REQUEST)

        winning_tickets = LotteryTicket.objects.filter(lottery=lottery, number=winning_number)
        print(winning_tickets)

        if winning_tickets.exists():
            total_prize = Decimal(lottery.total_revenue) * Decimal(0.9)
            admin = AdminProfile.objects.filter(is_superuser=True).first()  # find admin on top
            admin.main_wallet += Decimal(lottery.total_revenue) * Decimal(0.1) # add 10% on admin wallet
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
            admin.main_wallet += lottery.total_revenue
            admin.save()
        print(lottery.lottery_code)

        lottery.delete()

        Lottery.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(minutes=2)
        )

        return Response({'message': f'Lottery result declared {winning_number} and next lottery started'},
                        status=status.HTTP_200_OK)


class LotteryTransaction(APIView):
    def get(self, request):
        all = LotteryTicket.objects.all()
        serializer = LotteryTransactionSerializer(all, many=True)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class Profile(APIView):
    def get(self, request):
        user_id = self.request.query_params.get('user')
        user_transaction = self.request.query_params.get('transaction')

        if user_transaction == 'true':
            all = Transaction.objects.filter(user_id=user_id).first()
            serializer = TransactionSerializer(all)
            return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)

        user = UserProfile.objects.get(id=user_id)
        serializer = ProfileSerializer(user)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)
