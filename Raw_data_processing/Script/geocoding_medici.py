import json
import requests
import geojson
import time

# === CONFIG ===
API_KEY = "INSERISCI_LA_TUA_API_KEY"
INPUT_FILE = "medici_by_municipality_with_nuclei.json"
OUTPUT_FILE = "medici_geocoded_google.geojson"
FAILED_FILE = "indirizzi_non_trovati_google.txt"
COST_PER_REQUEST_USD = 0.005

# === GEOCODING FUNCTION (Google) ===
def google_geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    result = response.json()

    return

    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        return location['lng'], location['lat']
    else:
        return None, None

# === LOAD INPUT JSON ===
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

features = []
not_found = []
request_count = 0

for comune, values in data.items():
    for indirizzo in values["medici"]:
        full_address = f"{indirizzo}, {comune}, Lazio, Italia"
        
        request_count += 1

        continue 
        lon, lat = google_geocode(full_address)
        

        if lon is not None and lat is not None:
            point = geojson.Point((lon, lat))
            props = {
                "comune": comune,
                "indirizzo": indirizzo
            }
            features.append(geojson.Feature(geometry=point, properties=props))
        else:
            print(f"❌ Non trovato: {full_address}")
            not_found.append(f"{comune} - {indirizzo}")

        time.sleep(0.2)  # piccolo delay per evitare burst

# === SALVA GEOJSON ===
fc = geojson.FeatureCollection(features)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    geojson.dump(fc, f, ensure_ascii=False, indent=2)

# === SALVA NON TROVATI ===
if not_found:
    with open(FAILED_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(not_found))
    print(f"⚠️ Salvati {len(not_found)} indirizzi non trovati in: {FAILED_FILE}")

# === STAMPA RIEPILOGO ===
total_cost = request_count * COST_PER_REQUEST_USD
print(f"✅ Richieste totali: {request_count}")
print(f"💸 Costo stimato: {total_cost:.3f} USD (a 0,005 USD per richiesta)")
print(f"📍 File GeoJSON salvato: {OUTPUT_FILE}")
