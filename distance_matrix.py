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
from pyproj import Transformer

# Chiave API Google Maps
GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"

# File di cache per distanze
CACHE_FILE = "google_distances_transit_cache.json"

# Limiti Distance Matrix API
MAX_ELEMENTS = 100  # nuclei × scuole ≤ 100
MAX_ORIGINS = 25  # massimo 25 nuclei per batch
MAX_DESTINATIONS = 25  # massimo 25 scuole per batch

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# **1️⃣ Caricare il file JSON con scuole e nuclei**
with open("school_by_municipality_with_nuclei.json", "r", encoding="utf-8") as f:
    school_data = json.load(f)

# **2️⃣ Caricare il file con la popolazione e filtrare i comuni < 50.000 abitanti**
pop_df = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])
pop_df = pop_df.rename(columns={"ITTER107": "PRO_COM", "Territorio": "Comune", "Value": "Popolazione"})
pop_df["Comune"] = pop_df["Comune"].str.upper()

# Filtrare solo comuni con meno di 40.000 abitanti
filtered_comuni = pop_df[pop_df["Popolazione"] < 40000]["Comune"].tolist()

# **3️⃣ Caricare i centroidi dei nuclei urbani**
with open("Distance-project/Data_Italia/centroides_nucleos_urbanos.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

def convert_utm_to_wgs84(easting, northing):
    """
    Converte coordinate UTM (easting, northing) in coordinate geografiche WGS84 (lat, lon).
    """
    lon, lat = transformer.transform(easting, northing)  # X = Easting, Y = Northing
    #print(f"🛰️ Convertito UTM ({easting}, {northing}) -> WGS84 ({lat}, {lon})")
    return lat, lon  # Restituisce latitudine e longitudine

nuclei_centroidi = {}
for feature in centroidi_data["features"]:
    properties = feature["properties"]
    loc_id = str(properties["LOC21_ID"])  # Convertiamo a stringa per coerenza
    pop = properties.get("POP21", 0)  # Se il campo non esiste, assumiamo 0
    tipo = properties.get("TIPO_LOC", 0)

    if pop > 20 and (tipo == 1 or tipo == 2):  # Solo nuclei validi
        easting, northing = feature["geometry"]["coordinates"]  # UTM (X, Y)
        lat, lon = convert_utm_to_wgs84(easting, northing)  # Convertiamo in WGS84
        nuclei_centroidi[loc_id] = (lat, lon)  # Salviamo nel formato corretto

#print("Esempio di nuclei_centroidi:", nuclei_centroidi)

#print("Esempio di filtered_comuni:", filtered_comuni[:5])
#print("Esempio di school_data:", list(school_data.keys())[:5])

filtered_school_data = {
    comune: data for comune, data in school_data.items() if comune.upper() in filtered_comuni
}

# 🔹 Test: stampiamo un esempio
#print("Esempio di comune filtrato:", list(filtered_school_data.keys())[:5])

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



def get_distance_matrix(origins, destinations):
    """
    Ottiene le distanze tra una lista di origini (nuclei) e destinazioni (scuole) tramite Google API.
    """
    cache_key = f"{tuple(origins)}-{tuple(destinations)}"

    if cache_key in distance_cache:
        #print(f"📌 Usando cache per {cache_key}")
        print(f"🔹 Richiesta API con {len(origins)} origini e {len(destinations)} destinazioni.")
        
        if "rows" in distance_cache[cache_key]:
            #print(f"✅ Risultato ricevuto. Numero di origini nella risposta: {len(distance_cache[cache_key])}")
            #print(f"📍 Origini attese: {origins}")
            #print(f"📍 Origini ricevute: {distance_cache[cache_key].get('origin_addresses', [])}")

            return distance_cache[cache_key]
    
    #print(f"🔹 Richiesta API con {len(origins)} origini e {len(destinations)} destinazioni.")

    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "transit",
        "departure_time": 1741071600  # Considera il traffico attuale
    }

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    response = requests.get(url, params=params)
    data = response.json()

    time.sleep(1)

    #if "rows" in data:
        #print(f"✅ Risultato ricevuto. Numero di origini nella risposta: {len(data['rows'])}")
        #print(f"📍 Origini attese: {origins}")
        #print(f"📍 Origini ricevute: {data.get('origin_addresses', [])}")
    
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

    #k=0
    

    for comune, data in filtered_school_data.items():

        print(comune)

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
        origin_coords = [
            f"{lat},{lon}"
            for n in nuclei if str(n) in nuclei_centroidi
            for lat, lon in [nuclei_centroidi[str(n)]]
        ]
          
        destination_coords = [f"{lat},{lon}" for lat, lon in schools]

        # Suddividere in batch per rispettare i limiti API
        origin_batches = [origin_coords[i:i + MAX_ORIGINS] for i in range(0, len(origin_coords), MAX_ORIGINS)]
        destination_batches = [destination_coords[i:i + MAX_DESTINATIONS] for i in range(0, len(destination_coords), MAX_DESTINATIONS)]

        #if comune == "FORMIA":
            #print("N. of origins: " + str(len(origin_batches)))
            #print("N. of destinations: " + str(len(destination_batches)))

        # Iterare su ogni combinazione di batch di origini e destinazioni
        for origin_batch, destination_batch in itertools.product(origin_batches, destination_batches):
            
            if len(origin_batch) * len(destination_batch) > MAX_ELEMENTS:
                #print(f"⚠️ Batch troppo grande ({len(origin_batch)} x {len(destination_batch)}) per {comune}, suddividendolo...")

                # Definiamo i sottobatch ottimali
                max_origins_per_subbatch = MAX_ELEMENTS // len(destination_batch)
                max_destinations_per_subbatch = MAX_ELEMENTS // len(origin_batch)

                # Assicuriamoci che almeno 1 origine e 1 destinazione siano presenti
                max_origins_per_subbatch = max(1, max_origins_per_subbatch)
                max_destinations_per_subbatch = max(1, max_destinations_per_subbatch)

                # Creiamo nuovi batch più piccoli
                smaller_origin_batches = [origin_batch[i:i + max_origins_per_subbatch] for i in range(0, len(origin_batch), max_origins_per_subbatch)]
                smaller_destination_batches = [destination_batch[i:i + max_destinations_per_subbatch] for i in range(0, len(destination_batch), max_destinations_per_subbatch)]

                # 🔹 Dizionario temporaneo per accumulare i risultati di tutti i batch
                cumulative_results = {}

                reverse_nuclei_map = {f"{lat},{lon}": nucleo_id for nucleo_id, (lat, lon) in nuclei_centroidi.items()}


                # Iteriamo sui sottobatch
                for small_origin_batch, small_destination_batch in itertools.product(smaller_origin_batches, smaller_destination_batches):
                    if len(small_origin_batch) * len(small_destination_batch) <= MAX_ELEMENTS:

                        elementi = elementi+len(small_origin_batch) * len(small_destination_batch)

                        sub_result = get_distance_matrix(small_origin_batch, small_destination_batch)

                        if sub_result and "rows" in sub_result:
                            for i, origin in enumerate(small_origin_batch):
                                origin_id = reverse_nuclei_map.get(origin, origin)
                                if origin_id not in cumulative_results:
                                    cumulative_results[origin_id] = {}

                                for j, destination in enumerate(small_destination_batch):
                                    if j < len(sub_result["rows"][i]["elements"]):
                                        element = sub_result["rows"][i]["elements"][j]
                                        if element["status"] == "OK":
                                            distance = element["distance"]["value"]
                                            time_duration = element.get("duration_in_traffic", element.get("duration", {})).get("value", None)

                                            cumulative_results[origin_id][destination] = {
                                                "distanza_m": distance,
                                                "tempo_s": time_duration
                                            }

                # Ora aggiorniamo il dizionario globale con i risultati accumulati
                for origin_id, destinations in cumulative_results.items():
                    filtered_school_data[comune]["DISTANCE"] = filtered_school_data[comune].get("DISTANCE", {})
                    filtered_school_data[comune]["DISTANCE"][origin_id] = destinations

            else:
                elementi = elementi+len(origin_batch) * len(destination_batch)
                result = get_distance_matrix(origin_batch, destination_batch)
                

                if not result or "rows" not in result:
                    continue  # Salta se errore API

                # Assicuriamoci che "DISTANCE" sia inizializzata
                if "DISTANCE" not in filtered_school_data[comune]:
                    filtered_school_data[comune]["DISTANCE"] = {}

                # Creiamo il reverse map se non già definito
                reverse_nuclei_map = {f"{lat},{lon}": nucleo_id for nucleo_id, (lat, lon) in nuclei_centroidi.items()}

                for i, origin in enumerate(origin_batch):
                    origin_id = reverse_nuclei_map.get(origin, origin)  # Usa l'ID se disponibile

                    if origin_id not in filtered_school_data[comune]["DISTANCE"]:
                        filtered_school_data[comune]["DISTANCE"][origin_id] = {}

                    for j, destination in enumerate(destination_batch):
                        if j < len(result["rows"][i]["elements"]):
                            element = result["rows"][i]["elements"][j]
                            if element["status"] == "OK":
                                distance = element["distance"]["value"]
                                time_duration = element.get("duration_in_traffic", element.get("duration", {})).get("value", None)

                                filtered_school_data[comune]["DISTANCE"][origin_id][destination] = {
                                    "distanza_m": distance,
                                    "tempo_s": time_duration
                                }
                            else:
                                log_message = f"NO RESULT for: {origin} - {destination}\n"
                                print(log_message)  # Stampa in console
                                with open("distance_matrix_errors.log", "a", encoding="utf-8") as f:
                                    f.write(log_message)  # Scrive nel file

        #print(k)

        #if k > 20:
            #break
        
        


# **Esegui il processo di calcolo distanze**
process_municipality_distances()

# **Salva il file aggiornato con le distanze**
with open("school_by_municipality_with_distances_transit_complete.json", "w", encoding="utf-8") as f:
    json.dump(filtered_school_data, f, indent=4, ensure_ascii=False)


#print("✅ File aggiornato con le distanze salvato come 'school_by_municipality_with_distances_filtered.json'")
print("Elementi: ", elementi)