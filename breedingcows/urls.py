from django.urls import path
from . import views

urlpatterns = [
    path('', views.breeding_cows_list, name='breeding_cows_list'),
    path('breeding_cow/<int:pk>/', views.breeding_cow_detail, name='breeding_cow_detail'),
    path('breeding_cow/new/', views.breeding_cow_new, name='breeding_cow_new'),
    path('breeding_cow/<int:pk>/edit/', views.breeding_cow_edit, name='breeding_cow_edit'),
    path('api/breeding_cow/chart/data/', views.ChartData.as_view()),
    path('breeding_cow/<int:pk>/delete/', views.breeding_cow_delete, name='breeding_cow_delete'),
    path('breeding_cow/<int:pk>/notification/<str:notification_type>/', views.breeding_cow_notification, name='breeding_cow_notification'),
    path('breeding_cow/<int:pk>/dashboard/', views.breeding_cow_dashboard, name='breeding_cow_dashboard'),
    path('api/breeding_cow/<int:pk>/dashboard/', views.ChartData.as_view()),
]
