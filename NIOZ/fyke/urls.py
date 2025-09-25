from django.urls import path
from . import views


urlpatterns = [
    # Standard URL's
    path('', views.index, name='index'),
    path('exportdata/', views.exportdata, name='exportdata'),
    
    # Datacollection URL's
    path('datacollection/', views.datacollection_view, name='datacollection'),  # Data list page
    path('datacollection/new_record/', views.new_record_view, name='new_record'),  # Form page for adding new record
    path('datacollection/edit/<int:pk>/', views.edit_record_view, name='edit_record'),  # URL for editing a record
    path('datacollection/biotic/<int:pk>/', views.biotic, name='biotic'),  # Record biotic page
    
    # Catchlocations URL's
    path('catchlocations/', views.catchlocations, name='catchlocations'),
    path('catchlocations/new_location/', views.new_location, name='new_location'),
    path('catchlocations/edit_location/<int:pk>/', views.edit_location, name='edit_location'), 
    
    # Fishdetails URL's
    path('fishdetails/', views.fishdetails, name='fishdetails'),
    path('fishdetails/live-species-search/', views.species_search, name='species_search'),

    # Exportdata URL's
    path('abiotic_csv/<int:year>', views.abiotic_csv, name='fyke_abiotic'),
    path('biotic_csv/<int:year>', views.biotic_csv, name='fyke_biotic'),
    path('cutting_csv/<int:year>', views.cutting_csv, name='fyke_cutting'),
    path('stomach_csv/<int:year>', views.stomach_csv, name='fyke_stomach'),
]
