from rest_framework.generics import *
# from decimal import Decimal
from rest_framework import status, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView, Response
from .serializers import *
from django.db.models import Q, Count, F
from django.db import transaction
from collections import defaultdict
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
# from .helpers import *
from rest_framework.decorators import api_view
import random, string
from decimal import Decimal
from django.contrib.auth import authenticate

class Index(APIView):
    def get(self, request):
        pass