from django.urls import path
from . import views

urlpatterns = [
    path('sanitarybook/', views.sanitary_book_list, name='sanitary_book_list'),
    path('sanitarybook/new/', views.sanitary_book_new, name='sanitary_book_new'),
    path('sanitarybook/<int:pk>/edit/', views.sanitary_book_edit, name='sanitary_book_edit'),
    path('sanitarybook/<int:pk>/', views.sanitary_book_detail, name='sanitary_book_detail'),
]
