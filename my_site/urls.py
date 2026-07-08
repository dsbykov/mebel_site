from django.urls import path
from . import views

# app_name = 'my_site'

urlpatterns = [
    path('', views.home, name='home'),
    path('review/create/', views.create_review, name='create_review'),
]