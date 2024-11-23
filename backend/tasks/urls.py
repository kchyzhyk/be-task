from django.urls import path
from . import views
urlpatterns = [
    path('', views.geocode_address, name='geocode_address'),
]
