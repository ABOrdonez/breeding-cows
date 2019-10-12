from django.urls import path
from . import views

urlpatterns = [
    path('', views.breeding_cows_list, name='breeding_cows_list'),
]