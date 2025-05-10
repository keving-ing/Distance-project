import os
import json
import time
import pandas as pd
import requests


# === CONFIG ===
GOOGLE_MAPS_API_KEY = ""
GEOCODE_CACHE_FILE = "geocode_cache_pronto_soccorso.json"
INPUT_CSV = "Raw_data_processing/Raw_data/emergenza_prontoSoccorso.csv"
SLEEP_TIME = 1  # seconds

# === Cache ===
def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

geocode_cache = load_cache(GEOCODE_CACHE_FILE)

elementi = 0

# === Geocoding ===
def geocode_address(address):

    global elementi

    if address in geocode_cache:
        return geocode_cache[address]

    print(f"🌍 Geocoding: {address}")
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY
    }

    elementi = elementi + 1

    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
    time.sleep(SLEEP_TIME)

    data = response.json()
    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        lat_lon = (loc["lat"], loc["lng"])
        geocode_cache[address] = lat_lon
        with open(GEOCODE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(geocode_cache, f, indent=4)
        return lat_lon
    else:
        log_message = f"❌ Errore geocoding per '{address}': {data.get('status')}\n"
        print(log_message)
        with open("geocoding_errors_pronto_soccorso.log", "a", encoding="utf-8") as f:
            f.write(log_message)
        return None

# === Caricamento CSV ===
df = pd.read_csv(INPUT_CSV, delimiter=";")

# === Esecuzione geocoding ===
for idx, row in df.iterrows():
    indirizzo = row["STRUTTURA"] + ", " + row["Indirizzo"] + ", " + row["Località"]  # cambia il nome colonna se diverso
    geocode_address(indirizzo)

# === Salvataggio CSV per controllo visivo in QGIS ===
output_data = []

for address, (lat, lon) in geocode_cache.items():
    output_data.append({
        "indirizzo": address,
        "latitudine": lat,
        "longitudine": lon
    })

df_out = pd.DataFrame(output_data)
df_out.to_csv("pronto_soccorso_geocodificati.csv", index=False, encoding="utf-8")

print("📍 File 'pronto_soccorso_geocodificati.csv' esportato per QGIS.")
print(f"✅ Geocoding completato. Totale indirizzi geocodificati: {len(geocode_cache)} - elementi: {elementi}")
