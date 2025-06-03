import json
import os
import time
import requests
from math import radians, sin, cos, sqrt, atan2
from pyproj import Transformer

# === CONFIG ===
GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"
COMUNI_INPUT = "ps_by_municipality_with_nuclei.json"
CENTROIDI_FILE = "C:/Users/vehico/Documents/centroidi_salute.geojson"
GEOCODE_CACHE_FILE = "geocode_cache_pronto_soccorso.json"
OUTPUT_FILE = "ps_by_municipality_with_distances.json"
DISTANCE_MATRIX_CACHE_FILE = "distance_matrix_cache.json"

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4)



elementi = 0

if os.path.exists(DISTANCE_MATRIX_CACHE_FILE):
    distance_matrix_cache = load_json(DISTANCE_MATRIX_CACHE_FILE)
else:
    distance_matrix_cache = {}



def get_distance_matrix(origin, destinations):
    global elementi

    # Chiave per la cache
    cache_key = f"{origin}|{'|'.join(destinations)}"
    if cache_key in distance_matrix_cache:
        return distance_matrix_cache[cache_key]

    params = {
        "origins": origin,
        "destinations": "|".join(destinations),
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
        "departure_time": 1749027600
    }

    try:
        response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
        time.sleep(1)
        data = response.json()

        if data["status"] == "OK":
            distance_matrix_cache[cache_key] = data
            elementi += len(destinations)
            return data
        else:
            print(f"❌ Distance Matrix error: {data.get('status')}")
            return None
    except Exception as e:
        print("⚠️ Exception during request:", e)
        return None

# === Loading data ===
comuni = load_json(COMUNI_INPUT)
geocode_cache = load_json(GEOCODE_CACHE_FILE)
centroidi_data = load_json(CENTROIDI_FILE)

# Centroids for LOC21_ID
nuclei_centroidi = {}
for feat in centroidi_data["features"]:
    props = feat["properties"]
    loc_id = str(int(props["LOC21_ID"]))
    pop = props.get("POP21", 0)
    if pop > 0:
        easting, northing = feat["geometry"]["coordinates"]
        lat, lon = convert_utm_to_wgs84(easting, northing)
        nuclei_centroidi[loc_id] = (lat, lon)

# Pronto soccorso come lista (indirizzo + coordinate)
ospedali = [{"indirizzo": addr, "coord": coord} for addr, coord in geocode_cache.items()]

# === Calculating distances ===
for comune, data in comuni.items():
    print(comune)

    nuclei = data.get("nuclei", [])
    
    if "DISTANCE" not in comuni[comune]:
        comuni[comune]["DISTANCE"] = {}

    for nucleo_id in nuclei:
        nucleo_id_str = str(int(float(nucleo_id)))
        if nucleo_id_str not in nuclei_centroidi:
            continue

        lat_n, lon_n = nuclei_centroidi[nucleo_id_str]
        origin = f"{lat_n},{lon_n}"

        # Calculate Euclidean distances
        dists = []
        for osp in ospedali:
            lat_o, lon_o = osp["coord"]
            dist = euclidean_distance(lat_n, lon_n, lat_o, lon_o)
            dists.append((osp["indirizzo"], lat_o, lon_o, dist))

        # Select the 3 closest
        dists.sort(key=lambda x: x[3])
        top3 = dists[:3]

        destinations = [f"{lat},{lon}" for _, lat, lon, _ in top3]
        indirizzi_top3 = [addr for addr, _, _, _ in top3]

        result = get_distance_matrix(origin, destinations)

        
        if not result or "rows" not in result:
            continue

        comuni[comune]["DISTANCE"][nucleo_id_str] = {}

        for j, element in enumerate(result["rows"][0]["elements"]):
            if element["status"] == "OK":
                comuni[comune]["DISTANCE"][nucleo_id_str][indirizzi_top3[j]] = {
                    "distanza_m": element["distance"]["value"],
                    "tempo_s": element["duration"]["value"]
                }
            else:
                print(f"⚠️ No result for {origin} → {indirizzi_top3[j]}")


# === Saving ===
save_json(comuni, OUTPUT_FILE)
print("✅ Final file saved to:", OUTPUT_FILE, " - elements: ", elementi)
save_json(distance_matrix_cache, DISTANCE_MATRIX_CACHE_FILE)