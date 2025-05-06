import json
import requests
import pandas as pd
import os
import itertools
import time
from pyproj import Transformer
from math import radians, sin, cos, sqrt, atan2


#AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E

# === CONFIG ===
GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"
CACHE_FILE = "google_distances_medici_cache_ROMA.json"
GEOCODE_CACHE = "DATA_DISTANCIAS\geocode_cache_medici.json"
MAX_ELEMENTS = 100
MAX_ORIGINS = 25
MAX_DESTINATIONS = 25

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# === Cache ===
def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

distance_cache = load_cache(CACHE_FILE)
geocode_cache = load_cache(GEOCODE_CACHE)

elementi_geo = 0
# === Geocoding ===
def geocode_address(address):
    global elementi_geo

    if address in geocode_cache:
        return geocode_cache[address]

    #print(f"🌍 Geocoding: {address}")
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY
    }

    elementi_geo = elementi_geo + 1



    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
    time.sleep(1)
    data = response.json()
    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        geocode_cache[address] = (loc["lat"], loc["lng"])
        with open(GEOCODE_CACHE, "w", encoding="utf-8") as f:
            json.dump(geocode_cache, f, indent=4)
        return loc["lat"], loc["lng"]
    else:
        log_message = f"❌ Errore geocoding per '{address}': {data.get('status')}\n"
        print(log_message)
        with open("geocoding_errors_mediciROMA.log", "a", encoding="utf-8") as f:
            f.write(log_message)
        return None, None

# === Distance Matrix API ===
elementi = 0
def get_distance_matrix(origins, destinations):
    global elementi
    cache_key = f"{tuple(origins)}-{tuple(destinations)}"
    if cache_key in distance_cache:
        return distance_cache[cache_key]

    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
        "departure_time": 1746608400  # Considera il traffico attuale
    }

    elementi += len(origins) * len(destinations)


    response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
    data = response.json()
    time.sleep(1)

    if data["status"] == "OK":
        distance_cache[cache_key] = data
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(distance_cache, f, indent=4)
        return data
    else:
        log_message = f"❌ Errore Distance Matrix API per origins={origins} e destinations={destinations}: {data.get('status')}\n"
        print(log_message)
        with open("distance_matrix_errors_mediciROMA.log", "a", encoding="utf-8") as f:
            f.write(log_message)

# === Caricamento dati ===
with open("medici_by_municipality_with_nuclei_ROMA_OK.json", "r", encoding="utf-8") as f:
    medici_data = json.load(f)

with open("C:/Users/vehico/Documents/centroidi_salute.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

# === Centroidi dei nuclei urbani ===
nuclei_centroidi = {}
for feature in centroidi_data["features"]:
    props = feature["properties"]
    loc_id = str(int(props["LOC21_ID"]))
    pop = props.get("POP21", 0)
    if pop > 0:
        easting, northing = feature["geometry"]["coordinates"]
        lat, lon = convert_utm_to_wgs84(easting, northing)
        nuclei_centroidi[loc_id] = (lat, lon)

# === Calcolo distanze ===
for comune, data in medici_data.items():
    
    print(comune)

    nuclei = data.get("nuclei", [])
    medici = data.get("medici", [])

    if not nuclei or not medici:
        continue

    if "DISTANCE" not in medici_data[comune]:
        medici_data[comune]["DISTANCE"] = {}

    for nucleo_id in nuclei:
        nucleo_id_str = str(int(float(nucleo_id)))
        if nucleo_id_str not in nuclei_centroidi:
            continue

        lat_n, lon_n = nuclei_centroidi[nucleo_id_str]
        origin = f"{lat_n},{lon_n}"

        if len(medici) <= 3:
            destinations = medici
        else:
            coords_dist = []
            for medico in medici:
                lat_m, lon_m = geocode_address(medico)



                if lat_m is not None and lon_m is not None:
                    dist = euclidean_distance(lat_n, lon_n, lat_m, lon_m)
                    coords_dist.append((medico, dist))
            coords_dist.sort(key=lambda x: x[1])
            destinations = [m[0] for m in coords_dist[:3]]
        
        if (len([origin])*len(destinations)) > 100:
            print(comune)


        result = get_distance_matrix([origin], destinations)


        if not result or "rows" not in result:
            continue

        medici_data[comune]["DISTANCE"][nucleo_id_str] = {}

        for j, destination in enumerate(destinations):
            element = result["rows"][0]["elements"][j]
            if element["status"] == "OK":
                medici_data[comune]["DISTANCE"][nucleo_id_str][destination] = {
                    "distanza_m": element["distance"]["value"],
                    "tempo_s": element["duration"]["value"]
                }
            else:
                log_message = f"❌ NO RESULT for: {origin} → {destination}\n"
                print(log_message)
                with open("distance_matrix_errors_medici.log", "a", encoding="utf-8") as f:
                    f.write(log_message)





# === Salvataggio finale ===
with open("medici_by_municipality_with_distances_ROMA.json", "w", encoding="utf-8") as f:
    json.dump(medici_data, f, indent=4)

print("✅ Distanze calcolate e file salvato! - elementi:", elementi, " de geocoding: ", elementi_geo)
