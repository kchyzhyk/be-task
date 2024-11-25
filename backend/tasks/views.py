from django.shortcuts import render
from .api import fetch_geocode_address, get_utility_rates
from .models import GeocodeAddress, UtilityRate, WeekdaySchedule
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import calendar

weekday_schedule = {}

def geocode_address(request):
    address = ''
    error = ''
    costs = []
    data = []
    average_costs = []
    monthly_costs = []
    
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
            cost = calculate_energy_cost(pricing_matrix, 1000)
            most_likely_tariff, min_cost = calculate_most_likely_tariff(pricing_matrix, 1000)
            costs.append(cost)
            average_cost = calculate_average_rate(pricing_matrix)
            average_costs.append(average_cost)
            monthly_cost = calculate_monthly_energy_cost(pricing_matrix, 1000)
            monthly_costs.append(monthly_cost)
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
                "data": data,
                "costs": costs, 
                "average_costs": average_costs,
                # "most_likely_tariff": most_likely_tariff,
                # "min_cost": min_cost,
                "monthly_costs": monthly_costs, 
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
    return {
        "periods": periods,
        "month_schedule": month_schedule
    }
    


def calculate_energy_cost(data, total_consumption, escalator=4):
    period_hours = {}
    for month_data in data["month_schedule"]:
        for month, intervals in month_data.items():
            for interval in intervals:
                period = interval["period"]
                start_time = datetime.fromisoformat(interval["starttime"])
                end_time = datetime.fromisoformat(interval["endtime"])

                year = start_time.year
                month_number = start_time.month
                days_in_month = calendar.monthrange(year, month_number)[1]

                hours = (end_time - start_time).total_seconds() / 3600
                period_hours[period] = period_hours.get(period, 0) + (hours * days_in_month / 30)

    total_hours = sum(period_hours.values())
    period_energy = {period: (hours / total_hours) * total_consumption for period, hours in period_hours.items()}
    total_cost = 0
    for period, energy in period_energy.items():
        for tariff in data["periods"]:
            if tariff["value"] == period:
                max_usage = float(tariff["max_usage"]) if tariff["max_usage"] not in [None, "None"] else None
                rate = tariff["rate"]
                escalated_rate = rate * (1 + escalator / 100)
                if max_usage and energy > max_usage:
                    total_cost += max_usage * escalated_rate
                    energy -= max_usage

                total_cost += energy * escalated_rate
                break

    print(f"Общая стоимость для {total_consumption} кВт⋅ч с учётом escalator{escalator}: ${total_cost:.2f}")
    return total_cost


def calculate_average_rate(pricing_matrix):
    total_cost = 0
    total_consumption = 0

    for period_data in pricing_matrix["periods"]:
        period_value = int(period_data["value"])
        rate = period_data["rate"]
        max_usage = float(period_data["max_usage"]) if period_data["max_usage"] not in [None, "None"] else None
        if max_usage:
            consumption = max_usage
        else:
            consumption = 0 
        total_consumption += consumption
        if consumption > 0:
            cost_for_period = consumption * rate
            total_cost += cost_for_period
    if total_consumption > 0:
        average_rate_per_kWh = (total_cost / total_consumption) * 100
        print(f"Средняя стоимость за кВт⋅ч за год: {average_rate_per_kWh:.2f}¢")
        return average_rate_per_kWh
    # add tariff id
    else:
        return 0


def calculate_most_likely_tariff(pricing_matrix, total_consumption):
    most_likely_tariff = None
    min_cost = float('inf') # as infinity

    for tariff in pricing_matrix["periods"]:
        rate = tariff["rate"]
        max_usage = float(tariff["max_usage"]) if tariff["max_usage"] not in [None, "None"] else None

        if max_usage and total_consumption > max_usage:
            cost = max_usage * rate
            remaining_consumption = total_consumption - max_usage
            cost += remaining_consumption * rate
        else:
            cost = total_consumption * rate

        if cost < min_cost:
            min_cost = cost
            most_likely_tariff = tariff

    return most_likely_tariff, min_cost



def calculate_monthly_energy_cost(pricing_matrix, total_consumption):
    monthly_costs = []
    for tariff in pricing_matrix["periods"]:
        monthly_cost = []
        for month_data in pricing_matrix["month_schedule"]:
            for month, intervals in month_data.items():
                month_cost = 0

                period_hours = {}
                for interval in intervals:
                    period = interval["period"]
                    start_time = datetime.fromisoformat(interval["starttime"])
                    end_time = datetime.fromisoformat(interval["endtime"])

                    hours = (end_time - start_time).total_seconds() / 3600
                    period_hours[period] = period_hours.get(period, 0) + hours

                total_hours = sum(period_hours.values())
                period_energy = {period: (hours / total_hours) * total_consumption for period, hours in period_hours.items()}

                for period, energy in period_energy.items():
                    if tariff["value"] == period:
                        rate = tariff["rate"]
                        escalator = 4

                        escalated_rate = rate * (1 + escalator / 100)
                        month_cost += energy * escalated_rate

                monthly_cost.append(month_cost)
        monthly_costs.append(monthly_cost)

    return monthly_costs
