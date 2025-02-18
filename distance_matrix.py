#
# Copyright 2014 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import json
import requests
import pandas as pd
import geopandas as gpd
import os
import itertools
import time

# Chiave API Google Maps
GOOGLE_MAPS_API_KEY = ""

# File di cache per distanze
CACHE_FILE = "google_distances_cache.json"

# Limiti Distance Matrix API
MAX_ELEMENTS = 100  # nuclei × scuole ≤ 100
MAX_ORIGINS = 25  # massimo 25 nuclei per batch
MAX_DESTINATIONS = 25  # massimo 25 scuole per batch

# **1️⃣ Caricare il file JSON con scuole e nuclei**
with open("school_by_municipality_with_nuclei.json", "r", encoding="utf-8") as f:
    school_data = json.load(f)

# **2️⃣ Caricare il file con la popolazione e filtrare i comuni < 50.000 abitanti**
pop_df = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])
pop_df = pop_df.rename(columns={"ITTER107": "PRO_COM", "Territorio": "Comune", "Value": "Popolazione"})
pop_df["Comune"] = pop_df["Comune"].str.upper()

# Filtrare solo comuni con meno di 50.000 abitanti
filtered_comuni = pop_df[pop_df["Popolazione"] < 50000]["Comune"].tolist()

# **3️⃣ Caricare i centroidi dei nuclei urbani**
with open("Distance-project/Data_Italia/centroides_nucleos_urbanos.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

# Creare dizionario {LOC21_ID: (lat, lon)}
nuclei_centroidi = {}
for feature in centroidi_data["features"]:
    properties = feature["properties"]
    loc_id = str(properties["LOC21_ID"])  # Convertiamo a stringa per coerenza
    pop = properties.get("POP21", 0)  # Se il campo non esiste, assumiamo 0

    if pop >= 20:  # Solo i nuclei con almeno 20 abitanti
        lat, lon = feature["geometry"]["coordinates"][1], feature["geometry"]["coordinates"][0]
        nuclei_centroidi[loc_id] = (lat, lon)

#print("Esempio di nuclei_centroidi:", nuclei_centroidi)

print("Esempio di filtered_comuni:", filtered_comuni[:5])
print("Esempio di school_data:", list(school_data.keys())[:5])

filtered_school_data = {
    comune: data for comune, data in school_data.items() if comune.upper() in filtered_comuni
}

# 🔹 Test: stampiamo un esempio
print("Esempio di comune filtrato:", list(filtered_school_data.keys())[:5])

# 📂 Salviamo il JSON con i comuni sotto i 50.000 abitanti
with open("filtered_schools.json", "w", encoding="utf-8") as f:
    json.dump(filtered_school_data, f, indent=4, ensure_ascii=False)

print("✅ File 'filtered_schools.json' salvato con comuni < 50.000 abitanti!")

# Caricare la cache delle distanze
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        try:
            distance_cache = json.load(f)
        except json.JSONDecodeError:
            distance_cache = {}
else:
    distance_cache = {}

# **Funzione per chiamare l'API Google Distance Matrix**
def get_distance_matrix(origins, destinations):
    """
    Ottiene le distanze tra una lista di origini (nuclei) e destinazioni (scuole) tramite Google API.
    """
    cache_key = f"{tuple(origins)}-{tuple(destinations)}"
    if cache_key in distance_cache:
        print(f"📌 Usando cache per {cache_key}")
        return distance_cache[cache_key]

    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
        "departure_time": "now"  # Considera il traffico attuale
    }

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        distance_cache[cache_key] = data
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(distance_cache, f, indent=4, ensure_ascii=False)
        return data
    else:
        print(f"⚠️  Errore API: {data}")
        return None

elementi = 0

# **Funzione per calcolare le distanze per ogni comune**
def process_municipality_distances():

    
    global elementi
    

    for comune, data in filtered_school_data.items():
        nuclei = data.get("NUCLEOS", [])
        if not nuclei:
            print(f"⚠️  No nuclei per il comune: {comune}")
            continue  # Se non ci sono nuclei, passa al comune successivo

        # Ottenere le scuole del comune
        schools = {(s["LAT"], s["LONG"]) for cat in ["SCUOLA INFANZIA", "SCUOLA PRIMARIA", "SCUOLA PRIMO GRADO", "ISTITUTO COMPRENSIVO"] for s in data.get(cat, [])}

        if not schools:
            print(f"⚠️  No scool per il comune: {comune}")
            continue  # Se il comune non ha scuole, passa avanti

        
        # Convertire scuole e nuclei in coordinate
        origin_coords = [f"{nuclei_centroidi[str(n)][0]},{nuclei_centroidi[str(n)][1]}" for n in nuclei if str(n) in nuclei_centroidi]
        destination_coords = [f"{lat},{lon}" for lat, lon in schools]
        #print(origin_coords)
        #print(destination_coords)
        # Suddividere in batch per rispettare i limiti API
        origin_batches = [origin_coords[i:i + MAX_ORIGINS] for i in range(0, len(origin_coords), MAX_ORIGINS)]
        destination_batches = [destination_coords[i:i + MAX_DESTINATIONS] for i in range(0, len(destination_coords), MAX_DESTINATIONS)]

        # Iterare su ogni combinazione di batch di origini e destinazioni
        for origin_batch, destination_batch in itertools.product(origin_batches, destination_batches):
            if len(origin_batch) * len(destination_batch) > MAX_ELEMENTS:
                continue  # Salta batch non validi

            if len(origin_batch) > 10 or len(destination_batch) > 10:
                print(f" Comune: {comune} ")
                print(f" Chiamata API per {len(origin_batch)} nuclei e {len(destination_batch)} scuole...")

            elementi += (len(origin_batch) * len(destination_batch))
            

            #result = get_distance_matrix(origin_batch, destination_batch)

            #if not result:
            continue  # Salta se errore API

            # Salvare le distanze nel JSON
            for i, origin in enumerate(origin_batch):
                for j, destination in enumerate(destination_batch):
                    element = result["rows"][i]["elements"][j]
                    if element["status"] == "OK":
                        distance = element["distance"]["value"]  # Distanza in metri
                        time_duration = element["duration"]["value"]  # Tempo in secondi

                        filtered_school_data[comune]["DISTANZE"] = filtered_school_data[comune].get("DISTANZE", {})
                        filtered_school_data[comune]["DISTANZE"][origin] = filtered_school_data[comune]["DISTANZE"].get(origin, {})
                        filtered_school_data[comune]["DISTANZE"][origin][destination] = {
                            "distanza_m": distance,
                            "tempo_s": time_duration
                        }

            # **Attendere 2 secondo tra chiamate per evitare limite di rate API**
            time.sleep(2)

# **Esegui il processo di calcolo distanze**
process_municipality_distances()

# **Salva il file aggiornato con le distanze**
with open("school_by_municipality_with_distances.json", "w", encoding="utf-8") as f:
    json.dump(filtered_school_data, f, indent=4, ensure_ascii=False)


#print("✅ File aggiornato con le distanze salvato come 'school_by_municipality_with_distances_filtered.json'")
print("Elementi: ", elementi)