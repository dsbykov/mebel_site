from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# app_name = 'my_site'
urlpatterns = [
    path('', views.home, name='home'), 
]


