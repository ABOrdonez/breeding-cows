from django.urls import path
from . import views

urlpatterns = [
    path('diets/', views.diets_list, name='diets_list'),
    path('diets/<int:pk>/', views.diet_detail, name='diet_detail'),
    path('diets/new/', views.diet_new, name='diet_new'),
    path('diets/<int:pk>/edit/', views.diet_edit, name='diet_edit'),
    path('diets/api/chart/data/', views.ChartData.as_view()),
]
