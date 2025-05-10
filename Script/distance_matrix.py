import json
import requests
import pandas as pd
import geopandas as gpd
import os
import itertools
import time
from pyproj import Transformer

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"

# Cache file for distances
CACHE_FILE = "C:/Users/vehico/Documents/Thesis/Distance-project/DATA_DISTANCIAS/google_distances_transit_cache1.json"

# Distance Matrix API limits
MAX_ELEMENTS = 100  # nuclei × schools ≤ 100
MAX_ORIGINS = 25  # maximum 25 nuclei per batch
MAX_DESTINATIONS = 25  # maximum 25 schools per batch

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# **1️⃣ Load JSON file with schools and nuclei**
with open("C:/Users/vehico/Documents/Thesis/Distance-project/school_by_municipality_with_nuclei_ROMA_OK.json", "r", encoding="utf-8") as f:
    school_data = json.load(f)

# **2️⃣ Load population file and filter municipalities < 40,000 inhabitants**
pop_df = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])
print(pop_df.head(5))
pop_df = pop_df.rename(columns={"ITTER107": "PRO_COM", "Territorio": "Comune", "Value": "Popolazione"})
pop_df["Comune"] = pop_df["Comune"].str.upper()

# Filter only municipalities with less than 40,000 inhabitants
filtered_comuni = pop_df[pop_df["Popolazione"] < 40000]["Comune"].tolist()

# **3️⃣ Load urban nuclei centroids**
with open("C:/Users/vehico/Documents/centroides_rivisitato.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

def convert_utm_to_wgs84(easting, northing):
    """
    Converts UTM coordinates (easting, northing) to WGS84 geographic coordinates (lat, lon).
    """
    lon, lat = transformer.transform(easting, northing)  # X = Easting, Y = Northing
    return lat, lon  # Returns latitude and longitude

nuclei_centroidi = {}
for feature in centroidi_data["features"]:
    properties = feature["properties"]
    loc_id = str(properties["LOC21_ID"])  # Convert to string for consistency
    pop = properties.get("POP21", 0)  # Assume 0 if the field does not exist
    tipo = properties.get("TIPO_LOC", 0)
    provincia = properties.get("COD_UTS", 0)

    if pop > 0 and (tipo == 1 or tipo == 2) and provincia == 258:  # Only valid nuclei
        easting, northing = feature["geometry"]["coordinates"]  # UTM (X, Y)
        lat, lon = convert_utm_to_wgs84(easting, northing)  # Convert to WGS84
        nuclei_centroidi[loc_id] = (lat, lon)  # Save in the correct format

# Filter school data for municipalities with less than 40,000 inhabitants
filtered_school_data = {
    comune: data for comune, data in school_data.items() if comune.upper() in filtered_comuni
}

# Save the JSON with municipalities under 40,000 inhabitants
with open("filtered_schools.json", "w", encoding="utf-8") as f:
    json.dump(filtered_school_data, f, indent=4, ensure_ascii=False)

print("✅ File 'filtered_schools.json' saved with municipalities < 40,000 inhabitants!")

# Load distance cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        try:
            distance_cache = json.load(f)
        except json.JSONDecodeError:
            distance_cache = {}
else:
    distance_cache = {}

elementi = 0

def get_distance_matrix(origins, destinations):
    """
    Retrieves distances between a list of origins (nuclei) and destinations (schools) using Google API.
    """
    global elementi
    cache_key = f"{tuple(origins)}-{tuple(destinations)}"

    if cache_key in distance_cache:
        return distance_cache[cache_key]

    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "transit",
        "departure_time": 1744272000  # Consider current traffic
    }

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    elementi = elementi + len(origins) * len(destinations)
    response = requests.get(url, params=params)
    data = response.json()

    time.sleep(1)

    if data["status"] == "OK":
        distance_cache[cache_key] = data
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(distance_cache, f, indent=4, ensure_ascii=False)
        return data
    else:
        print(f"⚠️ API Error: {data}")
        return None

# **Function to calculate distances for each municipality**
def process_municipality_distances():
    global elementi

    for comune, data in filtered_school_data.items():
        print(comune)

        nuclei = data.get("NUCLEOS", [])
        if not nuclei:
            print(f"⚠️ No nuclei for the municipality: {comune}")
            continue  # Skip to the next municipality if no nuclei

        # Get schools in the municipality
        schools = {(s["LAT"], s["LONG"]) for cat in ["SCUOLA INFANZIA", "SCUOLA PRIMARIA", "SCUOLA PRIMO GRADO", "ISTITUTO COMPRENSIVO"] for s in data.get(cat, [])}

        if not schools:
            print(f"⚠️ No schools for the municipality: {comune}")
            continue  # Skip to the next municipality if no schools

        # Convert schools and nuclei to coordinates
        origin_coords = [
            f"{lat},{lon}"
            for n in nuclei if str(n) in nuclei_centroidi
            for lat, lon in [nuclei_centroidi[str(n)]]
        ]

        destination_coords = [f"{lat},{lon}" for lat, lon in schools]

        # Split into batches to respect API limits
        origin_batches = [origin_coords[i:i + MAX_ORIGINS] for i in range(0, len(origin_coords), MAX_ORIGINS)]
        destination_batches = [destination_coords[i:i + MAX_DESTINATIONS] for i in range(0, len(destination_coords), MAX_DESTINATIONS)]

        # Iterate over each combination of origin and destination batches
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

                        #elementi = elementi+len(small_origin_batch) * len(small_destination_batch)

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
                #elementi = elementi+len(origin_batch) * len(destination_batch)
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
        #if k > 20:
            #break
        
        


# **Esegui il processo di calcolo distanze**
process_municipality_distances()

# **Save the updated file with distances**
with open("school_by_municipality_with_distances_transit_complete_TP_Roma_ok.json", "w", encoding="utf-8") as f:
    json.dump(filtered_school_data, f, indent=4, ensure_ascii=False)

print("✅ File updated with distances saved as 'school_by_municipality_with_distances_transit_complete_TP_Roma_ok.json'")
print("Elements: ", elementi)