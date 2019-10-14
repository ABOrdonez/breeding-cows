from django.urls import path
from . import views

urlpatterns = [
    path('', views.breeding_cows_list, name='breeding_cows_list'),
    path('breeding_cow/<int:pk>/', views.breeding_cow_detail, name='breeding_cow_detail'),

]