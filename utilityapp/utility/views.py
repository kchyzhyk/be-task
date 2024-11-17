from django.shortcuts import render

from django.http import JsonResponse
from .models import Project, ProposalUtility
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings

@csrf_exempt
def get_utility_data(request, address, consumption_kwh, escalator_percentage):
    # Call OpenEI API to get utility tariffs
    API_URL = "https://api.openei.org/utility_rates?version=3"
    API_KEY = settings.OPENEI_API_KEY
    
    params = {
        'address': address,
        'approved': 'true',
        'is_default': 'true',
        'api_key': API_KEY,
    }
    response = requests.get(API_URL, params=params)
    data = response.json()

    # Assuming we get data with tariff info
    tariff_name = data.get('most_likely_tariff', {}).get('name')
    price_per_kwh = data.get('most_likely_tariff', {}).get('average_price')
    
    # Calculate cost (simple example using price)
    yearly_cost = price_per_kwh * consumption_kwh * 12

    # Create Project and ProposalUtility models
    user = request.user  # Assuming user is logged in
    project = Project.objects.create(
        user=user,
        address=address,
        consumption_kwh=consumption_kwh,
        escalator_percentage=escalator_percentage,
        tariff=tariff_name
    )

    ProposalUtility.objects.create(
        project=project,
        openei_id=data.get('id'),
        tariff_name=tariff_name,
        pricing_matrix=data.get('pricing_matrix')
    )

    # Return data as a response
    return JsonResponse({
        'tariff_name': tariff_name,
        'price_per_kwh': price_per_kwh,
        'yearly_cost': yearly_cost
    })
