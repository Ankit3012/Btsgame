from django.urls import path,include
from .views import *
urlpatterns = [
    path('index/',Index.as_view(),name='index'),


]