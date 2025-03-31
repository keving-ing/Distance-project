import requests
import re
import time

def get_trip(origin_lat, origin_lon, dest_lat, dest_lon, date='2025-03-28', time='09:00am', log_file=None):
    url = 'http://localhost:8080/otp/routers/default/plan'
    params = {
        'fromPlace': f'{origin_lat},{origin_lon}',
        'toPlace': f'{dest_lat},{dest_lon}',
        'time': time,
        'date': date,
        'mode': 'TRANSIT,WALK',
        'maxWalkDistance': 1000,
        'arriveBy': 'false'
    }

    response = requests.get(url, params=params)
    data = response.json()

    result = f"\n🔍 {origin_lat},{origin_lon} → {dest_lat},{dest_lon}\n"

    if 'plan' in data and data['plan'].get('itineraries'):
        itinerary = data['plan']['itineraries'][0]
        duration_minutes = int(itinerary['duration'] / 60)
        distance_km = round(sum(leg['distance'] for leg in itinerary['legs']) / 1000, 2)

        result += f"🟢 OTP trovato: {duration_minutes} minuti, {distance_km} km\n"
        for i, leg in enumerate(itinerary['legs']):
            mode = leg['mode']
            from_place = leg['from']['name']
            to_place = leg['to']['name']
            route = leg.get('route', '')
            agency = leg.get('agencyName', '')
            step = f"  {i+1}. {mode} da '{from_place}' a '{to_place}'"
            if route:
                step += f" con la linea '{route}'"
            if agency:
                step += f" ({agency})"
            result += step + "\n"
    else:
        result += "🔴 Nessun itinerario trovato da OTP.\n"

    print(result)
    if log_file:
        log_file.write(result + "\n")


# === Legge le coordinate dal file
pattern = r"NO RESULT for: ([\d\.-]+),([\d\.-]+) - ([\d\.-]+),([\d\.-]+)"
input_path = "C:/Users/vehico/Documents/Thesis/distance_matrix_errors1.log"
output_path = "otp_results_ROMA.txt"
with open(input_path, "r") as f, open(output_path, "w", encoding="utf-8") as log:
    lines = f.readlines()
    for line in lines:
        match = re.match(pattern, line)
        if match:
            lat1, lon1, lat2, lon2 = map(float, match.groups())
            get_trip(lat1, lon1, lat2, lon2, log_file=log)
            time.sleep(1)  # per non sovraccaricare OTP
