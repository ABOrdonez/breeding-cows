from django.urls import path
from . import views

urlpatterns = [
    path('contacts/', views.contacts_list, name='contacts_list'),
    path('contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('contacts/new/', views.contact_new, name='contact_new'),
    path('contacts/<int:pk>/edit/', views.contact_edit, name='contact_edit'),
]
