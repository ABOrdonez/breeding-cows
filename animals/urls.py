from django.urls import path
from . import views

urlpatterns = [
    path('animals/', views.animals_list, name='animals_list'),
    path('animals/<int:pk>/', views.animal_detail, name='animal_detail'),
    path('animals/<int:pk>/edit/', views.animal_edit, name='animal_edit'),
    path(
        '<int:breedingCowsPk>/animals/new/',
        views.animal_new,
        name='animal_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/diet/new/',
        views.animal_diet_new,
        name='animal_diet_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/palpation/new/',
        views.animal_palpation_new,
        name='animal_palpation_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/weaning/new/',
        views.animal_weaning_new,
        name='animal_weaning_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/reproductiontype/new/',
        views.animal_reproduction_type_new,
        name='animal_reproduction_type_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/reproductionexecution/new/',
        views.animal_reproduction_execution_new,
        name='animal_reproduction_execution_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/revision/new/',
        views.animal_reproduction_revision_new,
        name='animal_reproduction_revision_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/reproductionseparation/new/',
        views.animal_reproduction_separation_new,
        name='animal_reproduction_separation_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/reproductionsuccess/new/',
        views.animal_reproduction_success_new,
        name='animal_reproduction_success_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/rejected/new/',
        views.animal_rejected_new,
        name='animal_rejected_new'
    ),
    path(
        '<int:breedingCowsPk>/animals/delete/',
        views.animal_delete,
        name='animal_delete'
    ),
        path(
        '<int:breedingCowsPk>/animals/list/<str:animalType>/',
        views.animals_list,
        name='animals_list'
    ),
]
