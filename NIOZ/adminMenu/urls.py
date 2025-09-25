from django.urls import path
from . import views
from .views import adminMenu
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin Menu URL
    path('adminMenu/', views.users_view, name='users_view'),

    # Admin Menu User URL
    path('user/<int:pk>/', views.userinfo_view, name='userinfo_view'),

    # Admin Menu New User URL
    path('new_user/', views.new_user, name='new_user'),

    # Admin Menu change password URL
    path('change-password/<int:pk>/', views.change_password, name='change_password'),

    path('no_access/', views.no_access, name='no_access'),
]