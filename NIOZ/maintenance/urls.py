from django.urls import path
from . import views

# url patterns
urlpatterns = [
    path('', views.index, name='index'),
    path('species_list/', views.species_list, name='species_list'),  
    path('fishprogrammes/', views.fishprogrammes, name='fishprogrammes'),
    path('fishlocations/', views.fishlocations, name='fishlocations'),
    path('species/new/', views.species_create, name='species_create'),
    path('species/<int:species_id>/edit/', views.species_edit, name='species_edit'),
             ]
