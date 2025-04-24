import json
import requests
import pandas as pd
import os
import itertools
import time
from pyproj import Transformer

#AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E

# === CONFIGURAZIONI ===
GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"
CACHE_FILE = "google_distances_hospitals_cache_transit_ROMA.json"
MAX_ELEMENTS = 100
MAX_ORIGINS = 25
MAX_DESTINATIONS = 25

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

# === 1️⃣ Caricamento Dati ===
with open("C:/Users/vehico/Documents/Thesis/Distance-project/hospital_by_municipality_with_nuclei_ROMA_OK.json", "r", encoding="utf-8") as f:
    hospital_data = json.load(f)

pop_df = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])
pop_df = pop_df.rename(columns={"ITTER107": "PRO_COM", "Territorio": "Comune", "Value": "Popolazione"})
pop_df["Comune"] = pop_df["Comune"].str.upper()

# Filtrare solo comuni con meno di 40.000 abitanti
filtered_comuni = pop_df[pop_df["Popolazione"] < 40000]["Comune"].tolist()

with open("C:/Users/vehico/Documents/centroides_rivisitato.geojson", "r", encoding="utf-8") as f:
    centroidi_data = json.load(f)

df_ospedali = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/elencoospedali.csv")
df_ospedali['comune'] = df_ospedali['comune'].str.upper()

# === 2️⃣ Preparazione Centroidi Nuclei Urbani ===
nuclei_centroidi = {}
for feature in centroidi_data["features"]:
    props = feature["properties"]
    loc_id = str(int(props["LOC21_ID"]))
    pop = props.get("POP21", 0)
    if pop > 0:
        easting, northing = feature["geometry"]["coordinates"]
        lat, lon = convert_utm_to_wgs84(easting, northing)
        nuclei_centroidi[loc_id] = (lat, lon)

# === 3️⃣ Carica Cache ===
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        distance_cache = json.load(f)
else:
    distance_cache = {}

# === 4️⃣ Funzione Chiamata API ===

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
        "mode": "transit",
        "departure_time": 1745499600  # Considera il traffico attuale
    }

    elementi = elementi + (len(origins)*len(destinations))


    response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
    data = response.json()

    time.sleep(1)  # Rispetta i limiti API

    if data["status"] == "OK":
        distance_cache[cache_key] = data
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(distance_cache, f, indent=4)
        return data
    else:
        print(f"⚠️ Errore API: {data}")
        return None

# === 5️⃣ Calcolo Distanze ===
for comune, data in hospital_data.items():
    if comune not in filtered_comuni:
        continue

    nuclei = data.get("nuclei", [])
    ospedali_ids = data.get("ospedali", [])

    if not nuclei or not ospedali_ids:
        continue


    origin_coords = [
        f"{lat},{lon}"
        for n in nuclei
        if str(int(float(n))) in nuclei_centroidi
        for lat, lon in [nuclei_centroidi[str(int(float(n)))]]
    ]


    # Prepara destinazioni come stringhe "Nome, Comune, Provincia"
    destination_strs = []
    ospedale_map = {}  # Mappa per risalire agli ID

    for osp_id in ospedali_ids:
        osp_row = df_ospedali[df_ospedali['Id_struttura'] == osp_id]
        if osp_row.empty:
            continue
        osp_info = osp_row.iloc[0]
        dest = f"{osp_info['nome_struttura']}, {osp_info['comune']}, {osp_info['provincia']}"
        destination_strs.append(dest)
        ospedale_map[dest] = osp_id

    # Batch
    origin_batches = [origin_coords[i:i + MAX_ORIGINS] for i in range(0, len(origin_coords), MAX_ORIGINS)]
    destination_batches = [destination_strs[i:i + MAX_DESTINATIONS] for i in range(0, len(destination_strs), MAX_DESTINATIONS)]

    for origin_batch, destination_batch in itertools.product(origin_batches, destination_batches):
        if len(origin_batch) * len(destination_batch) > MAX_ELEMENTS:
            continue  # (Per semplicità ora saltiamo, puoi gestire i sotto-batch come nello script originale)

        result = get_distance_matrix(origin_batch, destination_batch)


        if not result or "rows" not in result:
            continue

        if "DISTANCE" not in hospital_data[comune]:
            hospital_data[comune]["DISTANCE"] = {}

        reverse_nuclei_map = {f"{lat},{lon}": nucleo_id for nucleo_id, (lat, lon) in nuclei_centroidi.items()}

        for i, origin in enumerate(origin_batch):
            origin_id = reverse_nuclei_map.get(origin)
            if not origin_id:
                continue

            if origin_id not in hospital_data[comune]["DISTANCE"]:
                hospital_data[comune]["DISTANCE"][origin_id] = {}

            for j, destination in enumerate(destination_batch):
                element = result["rows"][i]["elements"][j]
                if element["status"] == "OK":
                    hospital_data[comune]["DISTANCE"][origin_id][destination] = {
                        "distanza_m": element["distance"]["value"],
                        "tempo_s": element["duration"]["value"]
                    }
                else:
                    log_message = f"NO RESULT for: {origin} - {destination}\n"
                    print(log_message)  # Stampa in console
                    with open("distance_matrix_errors_hospital_ROMA.log", "a", encoding="utf-8") as f:
                        f.write(log_message)  # Scrive nel file


# === 6️⃣ Salvataggio Output ===
with open("hospital_by_municipality_with_distances_transit_ROMA.json", "w", encoding="utf-8") as f:
    json.dump(hospital_data, f, indent=4)

print("✅ Distanze calcolate e file salvato! - elementi: ", elementi)
