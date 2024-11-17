from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('get_utility_data/', views.get_utility_data, name='get_utility_data'),
    path('admin/', admin.site.urls),
    path('utility/', include('utility.urls')),
    path('api/get_tariff_data/', views.get_tariff_data, name='get_tariff_data'),
    
]