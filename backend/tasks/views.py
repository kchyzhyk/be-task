from django.shortcuts import render
from .api import fetch_geocode_address, get_utility_rates
from .models import GeocodeAddress, UtilityRate, WeekdaySchedule
from bs4 import BeautifulSoup
import requests

weekday_schedule = {}

def geocode_address(request):
    address = ''
    error = ''
    data = []
    
    if request.method == 'POST':
        address, error = fetch_geocode_address(request)
        if address:
            geocode_address = GeocodeAddress.objects.create(
                formatted_address=address
            )
        data = get_utility_rates()
        for item in data:
            tariffs = fetch_html_container(item['uri'],"#energy_rate_strux_table" )
            schedules = extract_periods_weekday(item['uri'])
            pricing_matrix = generate_period_schedule(tariffs, schedules)
            utility_rate = UtilityRate.objects.create(
                    geocode_address=geocode_address,
                    utility_name=item.get('utility'),
                    schedule_name=item.get('name'),
                    startdate=item.get('startdate'),
                    enddate=item.get('enddate'),
                    uri=item.get('uri'),
                    pricing_matrix = pricing_matrix
                )
            for month, values in weekday_schedule.items():
                WeekdaySchedule.objects.create(
                    utility_rate=utility_rate,
                    month=month,
                    values=values
                )
    return render(request, 'tasks/base.html', 
                {"address": address,
                "error": error,
                "data": data
                })

def fetch_html_container(url, container_selector):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.select_one(container_selector)
        
        return str(container) if container else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def extract_periods_weekday(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        data_element = soup.find('div', id='data-energyWeekdaySched')

        if data_element:
            data_string = data_element.get_text(strip=True)

            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            schedule = {}
            for i, month in enumerate(months):
                start_index = i * 24
                end_index = start_index + 24 

                month_data = data_string[start_index:end_index]
                subblocks = [month_data[j:j+1] for j in range(0, len(month_data), 1)]
                schedule[month] = subblocks
            return schedule
        else:
            print("Element with id='data-energyWeekdaySched' not found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def home(request):
    return render(request, 'tasks/base.html')


from datetime import datetime, timedelta

def generate_period_schedule(tariffs_html, schedule_json):
    soup = BeautifulSoup(tariffs_html, 'html.parser')
    tariffs = []
    rows = soup.select('#energy_rate_strux_table .strux_view_row')

    for row in rows:
        period = row.select_one('.strux_view_cell:nth-child(1)').text.strip()
        tier = row.select_one('.strux_view_cell:nth-child(2)').text.strip() 
        max_usage = row.select_one('.strux_view_cell:nth-child(3)').text.strip()
        max_usage_units = row.select_one('.strux_view_cell:nth-child(4)').text.strip()
        rate = row.select_one('.strux_view_cell:nth-child(5)').text.strip()
        adjustment = row.select_one('.strux_view_cell:nth-child(6)').text.strip()
        tariffs.append({
                'period': period,
                'tier': tier,
                'max_usage': max_usage if max_usage else None,
                'max_usage_units': max_usage_units,
                'rate': float(rate),
                'adjustment': float(adjustment)
            })
    
    periods = []
    
    for tariff in tariffs:
        value = tariff['period'] if tariff['period'] != "" else periods[-1]["value"] if periods else None
        periods.append({
            "value": value,
            "tier": tariff['tier'],
            "max_usage": tariff.get('max_usage'),
            "max_usage_units": tariff['max_usage_units'],
            "rate": tariff['rate'],
            "adjustments": tariff.get('adjustments', 0)
        })
    
    month_schedule = []
    
    for month, periods_in_month in schedule_json.items():
        month_data = {month.lower(): []}
        
        current_period = None
        start_time = None
        end_time = None
        for idx, period in enumerate(periods_in_month):
            day = idx // 24 + 1
            hour = idx % 24
            
            if period != current_period:
                if current_period is not None:
                    month_data[month.lower()].append({
                        "period": current_period,
                        "starttime": start_time.isoformat(),
                        "endtime": end_time.isoformat()
                    })

        current_period = period
        start_time = datetime(2024, list(schedule_json.keys()).index(month) + 1, day, hour, 0)
        end_time = start_time + timedelta(hours=1)
            
        if idx == len(periods_in_month) - 1 or periods_in_month[idx + 1] != period: 
            month_data[month.lower()].append({
                    "period": current_period,
                    "starttime": start_time.isoformat(),
                    "endtime": end_time.isoformat()
            })
        
        if len(month_data[month.lower()]) == 1:
            month_data[month.lower()] = [{
                "period": periods_in_month[0],
                "starttime": datetime(2024, list(schedule_json.keys()).index(month) + 1, 1, 0, 0).isoformat(),
                "endtime": datetime(2024, list(schedule_json.keys()).index(month) + 1, 1, 23, 59).isoformat()
            }]
        month_schedule.append(month_data)
    
    print({
            "periods": periods,
            "month_schedule": month_schedule
        })
    return {
        "periods": periods,
        "month_schedule": month_schedule
    }