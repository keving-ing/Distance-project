import json
import requests
from pyproj import Transformer
from math import radians, sin, cos, sqrt, atan2
import os

GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"
#"AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"

CACHE_FILE = "distanze_cache_medici.json"

# Trasformatore coordinate da UTM a WGS84
transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# Conversione coordinate UTM → WGS84
def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

# Distanza euclidea tra 2 coordinate geografiche
def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Cache per evitare chiamate duplicate
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        try:
            distance_cache = json.load(f)
        except json.JSONDecodeError:
            distance_cache = {}
else:
    distance_cache = {}


elementi = 0

# Distanza stradale da centroide a indirizzo medico
def get_real_distance(origin_coords, destination_address):
    global elementi
    key = f"{origin_coords[0]},{origin_coords[1]}-{destination_address}"
    if key in distance_cache:
        print(f"📌 Usata distanza cache per {destination_address}")
        return distance_cache[key]

    params = {
        "origins": f"{origin_coords[0]},{origin_coords[1]}",
        "destinations": destination_address,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving"
    }

    elementi = elementi + 1

    response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
    data = response.json()

   

    if "rows" in data and data["rows"][0]["elements"][0]["status"] == "OK":
        distance = data["rows"][0]["elements"][0]["distance"]["value"]
        distance_cache[key] = distance
        with open(CACHE_FILE, "w") as f:
            json.dump(distance_cache, f, indent=4)
        return distance

    print("❌ Errore distanza Google API:", data)
    return float("inf")

# Caricamento file
with open("medici_by_municipality_noDuplicati.json", "r", encoding="utf-8") as f:
    medici_by_comune = json.load(f)

with open("C:/Users/vehico/Documents/Thesis/centroidi_comuni.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

with open("C:/Users/vehico/Documents/Thesis/Distance-project/comuni_con_confinanti.json", "r", encoding="utf-8") as f:
    confini_comuni = json.load(f)

# Costruzione centroidi: {COMUNE: (lat, lon)}
centroidi = {}
for feature in centroidi_data["features"]:
    nome = feature["properties"]["COMUNE"].upper()
    x, y = feature["geometry"]["coordinates"]
    lat, lon = convert_utm_to_wgs84(x, y)
    centroidi[nome] = (lat, lon)

# Dizionario comuni confinanti
confinanti_dict = {item["COMUNE"].upper(): [c.upper() for c in item["confinanti"]] for item in confini_comuni}

# Comuni da assegnare
comuni_senza_medici = [com for com, indirizzi in medici_by_comune.items() if not indirizzi]

print(f"👨‍⚕️ Comuni senza medici: {len(comuni_senza_medici)}")

# Processo di assegnazione
for comune in comuni_senza_medici:
    centroide = centroidi.get(comune)
    if not centroide:
        print(f"⚠️ Centroide non trovato per {comune}")
        continue

    medici_confinanti = []
    for confinante in confinanti_dict.get(comune, []):
        medici_confinanti.extend(medici_by_comune.get(confinante, []))

    if not medici_confinanti:
        print(f"❌ Nessun medico nei comuni confinanti di {comune}")
        continue

    # Se più di 10, filtra i 10 più vicini usando distanza euclidea tra centroidi
    if len(medici_confinanti) > 10:
        comuni_medici = []
        for confinante in confinanti_dict.get(comune, []):
            if confinante in centroidi and medici_by_comune.get(confinante):
                distanza = euclidean_distance(*centroide, *centroidi[confinante])
                for indirizzo in medici_by_comune[confinante]:
                    comuni_medici.append((indirizzo, distanza))
        # Prendi i 10 medici con comune più vicino
        comuni_medici.sort(key=lambda x: x[1])
        medici_confinanti = [m[0] for m in comuni_medici[:10]]

    # Calcola distanza stradale per ciascun medico
    min_dist = float("inf")
    best_medico = None
    for medico in medici_confinanti:
        distanza = get_real_distance(centroide, medico)

        if distanza < min_dist:
            min_dist = distanza
            best_medico = medico

    if best_medico:
        medici_by_comune[comune].append(best_medico)
        print(f"✅ Assegnato medico a {comune}: {best_medico}")


# Salva il nuovo file JSON
with open("medici_assegnati.json", "w", encoding="utf-8") as f:
    json.dump(medici_by_comune, f, ensure_ascii=False, indent=4)

print("📁 File aggiornato salvato come 'medici_assegnati.json' - elementi: ", elementi)
