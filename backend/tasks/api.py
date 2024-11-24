import requests
from django.conf import settings
import urllib.parse
from datetime import datetime

GEOCODING_API_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
OPENEI_URL = "https://api.openei.org/utility_rates?version=7&format=json"
    
context = {}

def fetch_geocode_address(request):
    address = request.POST.get('address')

    if address:
        try:
            geocoding_url = f"{GEOCODING_API_BASE_URL}?address={address}&key={settings.GEOCODING_API_KEY}"

            response = requests.get(geocoding_url)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    result = data['results'][0]
                    context['address'] = result['formatted_address']
                else:
                    context['error'] = f"Geocoding API error: {data['status']}"
            else:
                context['error'] = f"Error: Received status code {response.status_code} from the API."
        except requests.exceptions.RequestException as e:
            context['error'] = f"An error occurred while trying to fetch geocoding data: {str(e)}"
    else:
        context['error'] = "No address provided. Please enter an address."


    return context.get('address', ''), context.get('error', '')


def get_utility_rates():
    encoded_address = urllib.parse.quote(context['address'])
    url = f"{OPENEI_URL}&api_key={settings.OPENEI_API_KEY}&address={encoded_address}&orderby=startdate&direction=desc&approved=true&is_default=true"
    response = requests.get(url) 
    last_day_of_2021 = datetime(2021, 12, 31, 23, 59, 59)
    last_day_timestamp = int(last_day_of_2021.timestamp())
    if response.status_code == 200:
        data = response.json()
        filtered_data = [
            {
                **item,
                'startdate': format_timestamp(item['startdate']),  
                'enddate': format_timestamp(item['enddate']) if item.get('enddate') else None
            }
            for item in data.get('items', [])
            if item['startdate'] > last_day_timestamp
        ]
        return filtered_data
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        print("Response text:", response.text)
        return {"error": f"HTTP {response.status_code}"}
    
    
from datetime import datetime

def format_timestamp(unix_timestamp):
    if isinstance(unix_timestamp, int):
        try:
            return datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error formatting timestamp: {e}")
            return None
        return None