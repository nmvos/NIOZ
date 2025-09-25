from django.contrib import admin
from django.urls import path, include
from maintenance import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('LoginSysteem.urls')),
    path('', include('adminMenu.urls')),
    path('fyke/', include('fyke.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('adminMenu/', include('adminMenu.urls')),
    path('help/', include('help.urls')),

]
