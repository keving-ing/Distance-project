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
from math import sqrt
from pyproj import Transformer
import os
from math import radians, sin, cos, sqrt, atan2
import sys

# Chiave API di Google
GOOGLE_MAPS_API_KEY = "AIzaSyA5LyRBjEJ15vUmO5yHGX30tpEYN_OiiGo"

# File di cache per le distanze
CACHE_FILE = "distanze_cache.json"

#api_called = False

# Creiamo il trasformatore da UTM (EPSG:32632) a WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# Funzione per convertire le coordinate UTM in WGS84
def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon  

# Caricare la cache delle distanze se esiste
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        try:
            distance_cache = json.load(f)
            print("ok")
        except json.JSONDecodeError:
            distance_cache = {}
else:
    distance_cache = {}

# Funzione per calcolare la distanza reale tramite Google Distance Matrix API
def get_real_distance(origin, destination):
    #global api_called
    #if api_called:
        #return float("inf")  # Evitiamo altre chiamate


    if destination[0] > 90 or destination[1] > 180:  # Valori troppo alti indicano UTM
        destination = convert_utm_to_wgs84(destination[1], destination[0])

    # Creiamo una chiave univoca per la cache (es. "lat1,lon1-lat2,lon2")
    key = f"{origin[0]},{origin[1]}-{destination[0]},{destination[1]}"

    # Controlliamo se la distanza è già stata calcolata
    if key in distance_cache:
        #print(f"📌 Usando la distanza salvata per {key}")
        return distance_cache[key]

    # Formattazione corretta per Google API
    origin_str = f"{origin[0]},{origin[1]}"
    destination_str = f"{destination[0]},{destination[1]}"

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin_str,
        "destinations": destination_str,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving"
    }

    response = requests.get(url, params=params)
    data = response.json()

    #print(data)

    #api_called = True  # Segna che l'API è stata chiamata

    if "rows" in data and data["rows"] and "elements" in data["rows"][0] and data["rows"][0]["elements"]:
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":

            distance_cache[key] = element["distance"]["value"]  # Salviamo nella cache
            # Aggiorniamo il file JSON con la cache aggiornata
            with open(CACHE_FILE, "w") as f:
                json.dump(distance_cache, f, indent=4)
            return element["distance"]["value"]  # Distanza in metri
        
    
    print("params: ", params)
    print("ERROR: ", data)
    #sys.exit("Script interrotto per verifica.")
    return float("inf")

def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Raggio della Terra in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Caricare i dati dai file JSON
with open("C:/Users/vehico/Documents/Thesis/schools_by_urban_core.json", "r") as f:
    scuole_comuni = json.load(f)

with open("C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/centroides_nucleos_urbanos.geojson", "r") as f:
    centroidi_data = json.load(f)

with open("C:/Users/vehico/Documents/Thesis/nuclei_con_confinanti.json", "r") as f:
    confini_comuni = json.load(f)

# Creare un dizionario {comune: coordinate}
centroidi = {}
for feature in centroidi_data["features"]:
    nome_comune = str(feature["properties"]["LOC21_ID"])
    easting, northing = feature["geometry"]["coordinates"]
    lat, lon = convert_utm_to_wgs84(easting, northing)  # Conversione da UTM a WGS84
    centroidi[nome_comune] = (lat, lon)  # Salviamo nel formato corretto



# Creare un dizionario {comune: comuni confinanti}
confinanti_dict = {str(item["LOC21_ID"]): [str(c) for c in item["confinanti"]] for item in confini_comuni}

#comune_p = "6009139999.999999"
#print(confinanti_dict.get(comune_p, []))

def find_nearest_school(comune, categoria, visited=None, depth=0):
    """
    Cerca ricorsivamente la scuola più vicina per una determinata categoria,
    esplorando i comuni confinanti fino a trovarne almeno una.
    
    :param comune: Nome del comune da analizzare
    :param categoria: Categoria di scuola da cercare
    :param visited: Set di comuni già visitati per evitare cicli
    :param depth: Profondità della ricerca (evita loop infiniti)
    :return: La scuola più vicina trovata (o None se nessuna scuola disponibile)
    """
    if visited is None:
        visited = set()
    
    # Evitiamo di visitare due volte lo stesso comune
    if comune in visited:
        return None
    
    visited.add(comune)

    # Cerchiamo scuole nei confinanti
    scuole_confinanti = []
    
    for comune_confinante in confinanti_dict.get(comune, []):
        if comune_confinante in scuole_comuni and categoria in scuole_comuni[comune_confinante]:
            scuole_confinanti.extend(scuole_comuni[comune_confinante][categoria])

    if len(scuole_confinanti) == 1:
        return scuole_confinanti[:1]
    
    if len(scuole_confinanti) > 10:
        # Se ci sono più di 10 scuole, filtriamo con distanza euclidea
            centro = centroidi.get(comune)
            if centro:
                scuole_confinanti.sort(key=lambda s: euclidean_distance(centro[0], centro[1], s["LAT"], s["LONG"]))
                scuole_confinanti = scuole_confinanti[:10]

    # Se troviamo scuole, selezioniamo la più vicina usando la distanza reale
    if scuole_confinanti:
        centro = centroidi.get(comune)
        if centro:
            min_dist = float("inf")
            nearest_school = None
            for scuola in scuole_confinanti:
                dist = get_real_distance(centro, (scuola["LAT"], scuola["LONG"]))
                if dist < min_dist:
                    min_dist = dist
                    nearest_school = scuola
            return nearest_school

    # Se non troviamo scuole, cerchiamo nei confinanti dei confinanti (chiamata ricorsiva)
    if depth < 5:  # Limitiamo la profondità per evitare loop infiniti
        for comune_confinante in confinanti_dict.get(comune, []):
            nearest_school = find_nearest_school(comune_confinante, categoria, visited, depth + 1)
            if nearest_school:
                return nearest_school

    # Se dopo la ricerca non troviamo nulla, restituiamo None
    return None


for comune, categorie in scuole_comuni.items():

    # Se il comune ha un ISTITUTO COMPRENSIVO, ha già tutte le scuole
    if "ISTITUTO COMPRENSIVO" in categorie and categorie["ISTITUTO COMPRENSIVO"]:
        continue

    for categoria, scuole in categorie.items():

        # Se il comune ha già scuole per quella categoria, non serve cercare
        if scuole:
            continue

        # 🏫 CERCHIAMO LA SCUOLA PIÙ VICINA RICORSIVAMENTE
        nearest_school = find_nearest_school(comune, categoria)

        if nearest_school:
            scuole_comuni[comune][categoria].append(nearest_school)
        else:
            print(f"⚠️  Nessuna scuola trovata per {comune} - {categoria}.")

    break 

# Salvare il nuovo JSON con le scuole assegnate
with open("nucleos_school_complete.json", "w") as f:
    json.dump(scuole_comuni, f, indent=4)

print("File aggiornato salvato.")
