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

import csv
import json
import googlemaps

# Inserisci la tua Google Maps API Key
API_KEY = ""
gmaps = googlemaps.Client(key=API_KEY)

def geocode_address(address):
    """Ottiene latitudine e longitudine da un indirizzo usando Google Maps Geocoding API"""
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"Errore nella geocodifica {address}: {e}")
    return None, None

def process_csv(input_csv, output_geojson):
    """Legge un CSV, ottiene la geolocalizzazione per ogni indirizzo e salva i risultati in un GeoJSON"""
    features = []
    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')  
        for row in reader:
            address = (row.get("INDIRIZZOSCUOLA") or "") + ", " + (row.get("DESCRIZIONECOMUNE") or "") + ", Italia"
            lat, lng = geocode_address(address) if address.strip() else (None, None)
            
            if lat is not None and lng is not None:
                feature = {
                    "type": "Feature", "properties": {"CODICEISTITUTORIFERIMENTO": row.get("CODICEISTITUTORIFERIMENTO"), "DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA": row.get("DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA"), "DESCRIZIONECOMUNE": row.get("DESCRIZIONECOMUNE")}, "geometry": {"type": "Point","coordinates": [lng, lat]}
                }
                features.append(feature)
    
    geojson_data = {
        "type": "FeatureCollection",
        "name": "scuole_geocodificate",
        "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4326" } },
        "features": features
    }
    
    # Salva il file in formato GeoJSON
    with open(output_geojson, 'w', encoding='utf-8') as geojsonfile:
        json.dump(geojson_data, geojsonfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_csv = "C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/scuole_lazio_filtrate.csv"  # Cambia il percorso del CSV
    output_geojson = "geocoded_locations_school.geojson"
    process_csv(input_csv, output_geojson)
    print(f"Dati geocodificati salvati in {output_geojson}")
