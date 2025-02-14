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
from math import radians, cos, sin, sqrt, atan2

API_KEY = "AIzaSyApZ-fXlAG9y8JMs3Ecz-FnCIt52jJ7Kcs"
GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

# Carica i file JSON
with open("scuole_per_comune.json", "r") as f:
    scuole_per_comune = json.load(f)
with open("centroidi_comuni.json", "r") as f:
    centroidi_comuni = json.load(f)
with open("confini_comuni.json", "r") as f:
    confini_comuni = json.load(f)

# Funzione per calcolare la distanza euclidea tra due punti geografici
def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Raggio della Terra in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Funzione per ottenere distanze tramite Google Distance Matrix API
def get_distances(origins, destinations):
    origins_str = "|".join([f"{lat},{lon}" for lat, lon in origins])
    destinations_str = "|".join([f"{lat},{lon}" for lat, lon in destinations])
    params = {
        "origins": origins_str,
        "destinations": destinations_str,
        "key": API_KEY
    }
    response = requests.get(GOOGLE_MAPS_URL, params=params)
    data = response.json()
    distances = []
    if "rows" in data:
        for row in data["rows"]:
            distances.append([elem["distance"]["value"] if "distance" in elem else float("inf") for elem in row["elements"]])
    return distances

# Mappatura centroidi per comune
centroidi_dict = {f["properties"]["COMUNE"].upper(): f["geometry"]["coordinates"][::-1] for f in centroidi_comuni["features"]}
# Mappatura confini per comune
confini_dict = {c["COMUNE"].upper(): c["confinanti"] for c in confini_comuni}

# Analisi per ogni comune
for comune, dati_scuole in scuole_per_comune.items():
    comune_upper = comune.upper()
    if "ISTITUTO COMPRENSIVO" in dati_scuole and dati_scuole["ISTITUTO COMPRENSIVO"]:
        continue  # Ha un istituto comprensivo, quindi consideriamo che abbia tutte le scuole
    
    categorie_mancanti = [c for c, scuole in dati_scuole.items() if not scuole]
    comuni_confinanti = confini_dict.get(comune_upper, [])
    
    for categoria in categorie_mancanti:
        scuole_trovate = []
        
        for comune_conf in comuni_confinanti:
            if comune_conf in scuole_per_comune:
                scuole_trovate.extend(scuole_per_comune[comune_conf].get(categoria, []))
        
        if len(scuole_trovate) > 10:
            # Se ci sono più di 10 scuole, filtriamo con distanza euclidea
            centro = centroidi_dict.get(comune_upper)
            if centro:
                scuole_trovate.sort(key=lambda s: euclidean_distance(centro[0], centro[1], s["LAT"], s["LONG"]))
                scuole_trovate = scuole_trovate[:10]
        
        # Ora usiamo Google Maps Distance Matrix API per affinare la selezione
        if scuole_trovate:
            centro = centroidi_dict.get(comune_upper)
            if centro:
                origins = [centro]
                destinations = [(s["LAT"], s["LONG"]) for s in scuole_trovate]
                distanze = get_distances(origins, destinations)
                if distanze:
                    scuole_trovate = [scuole_trovate[i] for i in sorted(range(len(distanze[0])), key=lambda k: distanze[0][k])[:5]]
        
        scuole_per_comune[comune][categoria] = scuole_trovate

# Salvataggio del file JSON aggiornato
with open("scuole_aggiornate.json", "w") as f:
    json.dump(scuole_per_comune, f, indent=4)
