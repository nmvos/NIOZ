from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Root route of the help app
]