import json
import requests
import pandas as pd
import os
import itertools
import time
from pyproj import Transformer


# "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"
# === CONFIG ===
GOOGLE_MAPS_API_KEY = ""
CACHE_FILE = "google_distances_medici_cache.json"
MAX_ELEMENTS = 100
MAX_ORIGINS = 25
MAX_DESTINATIONS = 25

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

# === Loading data ===
with open("medici_by_municipality_with_nuclei_ROMA_OK.json", "r", encoding="utf-8") as f:
    medici_data = json.load(f)

with open("C:/Users/vehico/Documents/centroides_rivisitato.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

# === Building centroid dictionary ===
nuclei_centroidi = {}
for feature in centroidi_data["features"]:
    props = feature["properties"]
    loc_id = str(int(props["LOC21_ID"]))
    pop = props.get("POP21", 0)
    if pop > 0:
        easting, northing = feature["geometry"]["coordinates"]
        lat, lon = convert_utm_to_wgs84(easting, northing)
        nuclei_centroidi[loc_id] = (lat, lon)

# === Cache ===
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        distance_cache = json.load(f)
else:
    distance_cache = {}

# === Function for Distance Matrix API call ===
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
        "mode": "driving"
    }

    elementi += len(origins) * len(destinations)

    return

    response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
    data = response.json()
    time.sleep(1)

    if data["status"] == "OK":
        distance_cache[cache_key] = data
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(distance_cache, f, indent=4)
        return data
    else:
        print(f"⚠️ API Error: {data}")
        return None

# === Calculating distances ===
for comune, data in medici_data.items():
    nuclei = data.get("nuclei", [])
    medici = data.get("medici", [])

    if not nuclei or not medici:
        continue

    origin_coords = [
        f"{lat},{lon}"
        for n in nuclei
        if str(int(float(n))) in nuclei_centroidi
        for lat, lon in [nuclei_centroidi[str(int(float(n)))]]
    ]

    destination_strs = medici

    origin_batches = [origin_coords[i:i + MAX_ORIGINS] for i in range(0, len(origin_coords), MAX_ORIGINS)]
    destination_batches = [destination_strs[i:i + MAX_DESTINATIONS] for i in range(0, len(destination_strs), MAX_DESTINATIONS)]

    for origin_batch, destination_batch in itertools.product(origin_batches, destination_batches):
        if len(origin_batch) * len(destination_batch) > MAX_ELEMENTS:
            print("SKIPPING - ", comune, " ", str(len(origin_batch) * len(destination_batch)))
            continue

        result = get_distance_matrix(origin_batch, destination_batch)
        continue 
        if not result or "rows" not in result:
            continue

        if "DISTANCE" not in medici_data[comune]:
            medici_data[comune]["DISTANCE"] = {}

        reverse_nuclei_map = {f"{lat},{lon}": nucleo_id for nucleo_id, (lat, lon) in nuclei_centroidi.items()}

        for i, origin in enumerate(origin_batch):
            origin_id = reverse_nuclei_map.get(origin)
            if not origin_id:
                continue

            if origin_id not in medici_data[comune]["DISTANCE"]:
                medici_data[comune]["DISTANCE"][origin_id] = {}

            for j, destination in enumerate(destination_batch):
                element = result["rows"][i]["elements"][j]
                if element["status"] == "OK":
                    medici_data[comune]["DISTANCE"][origin_id][destination] = {
                        "distanza_m": element["distance"]["value"],
                        "tempo_s": element["duration"]["value"]
                    }
                else:
                    log_message = f"❌ NO RESULT for: {origin} → {destination}\n"
                    print(log_message)
                    with open("distance_matrix_errors_medici.log", "a", encoding="utf-8") as f:
                        f.write(log_message)

# === Final save ===
with open("medici_by_municipality_with_distances.json", "w", encoding="utf-8") as f:
    json.dump(medici_data, f, indent=4)

print("✅ Distances calculated and file saved! - elements: ", elementi)
