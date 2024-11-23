from django.shortcuts import render
from .api import fetch_geocode_address, get_utility_rates

def geocode_address(request):
    address = ''
    latitude = ""
    longitude = ''
    error = ''
    
    if request.method == 'POST':
        address, latitude, longitude, error = fetch_geocode_address(request)
        data = get_utility_rates()
        
    
    return render(request, 'tasks/base.html', 
                {"address": address,
                'latitude': latitude, 
                'longitude': longitude, 
                "error": error,
                "data": data
                })

def home(request):
    return render(request, 'tasks/base.html')
