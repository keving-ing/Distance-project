import json
import requests
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
import os
import zipfile

# === CONFIGURAZIONI ===
GOOGLE_MAPS_API_KEY = "INSERISCI_LA_TUA_API_KEY"
CACHE_FILE = "distanze_ospedali_cache.json"

# === Trasformazione Coordinate ===
transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

# === Caricamento Dati ===
print("📂 Caricamento dati...")

# Comuni
comuni_zip = "C:/Users/vehico/Documents/Thesis/comuni.zip"
comuni_folder = "C:/Users/vehico/Documents/Thesis/comuni"
with zipfile.ZipFile(comuni_zip, 'r') as zip_ref:
    zip_ref.extractall(comuni_folder)
comuni_shp_file = [f for f in os.listdir(comuni_folder) if f.endswith(".shp")][0]
gdf_comuni = gpd.read_file(os.path.join(comuni_folder, comuni_shp_file))
gdf_comuni['COMUNE'] = gdf_comuni['COMUNE'].str.upper()

# Dizionari di supporto
cod_uts_dict = dict(zip(gdf_comuni['PRO_COM'], gdf_comuni['COD_UTS']))
nome_comuni_dict = dict(zip(gdf_comuni['PRO_COM'], gdf_comuni['COMUNE']))

# Popolazione
df_pop = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv")
df_pop['Territorio'] = df_pop['Territorio'].str.upper()
popolazione_dict = dict(zip(df_pop['Territorio'], df_pop['Value']))

# Ospedali
df_ospedali = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/elencoospedali.csv")
df_ospedali['comune'] = df_ospedali['comune'].str.upper()

# Ospedali assegnati ai comuni
with open("Raw_data_processing/DATA/hospitals_by_municipality.json", "r") as f:
    ospedali_comuni = json.load(f)

# Centroidi Nuclei Urbani
with open("C:/Users/vehico/Documents/centroidi_salute.geojson", "r") as f:
    nuclei_data = json.load(f)

# Carica cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        distance_cache = json.load(f)
else:
    distance_cache = {}

# === Definizione Liste ASL Roma ===
asl_roma_dict = {}

asl_rm_f = [
    "ALLUMIERE", "ANGUILLARA SABAZIA", "BRACCIANO", "CAMPAGNANO DI ROMA", "CANALE MONTERANO", 
    "CAPENA", "CASTELNUOVO DI PORTO", "CERVETERI", "CIVITAVECCHIA", "CIVITELLA SAN PAOLO",
    "FIANO ROMANO", "FILACCIANO", "FORMELLO", "LADISPOLI", "MAGLIANO ROMANO", "MANZIANA", 
    "MAZZANO ROMANO", "MORLUPO", "NAZZANO", "PONZANO ROMANO", "RIANO", "RIGNANO FLAMINIO", 
    "SACROFANO", "SANT'ORESTE", "SANTA MARINELLA", "TOLFA", "TORRITA TIBERINA", "TREVIGNANO ROMANO"
]

asl_rm_g = [
    "AFFILE", "AGOSTA", "ANTICOLI CORRADO", "ARCINAZZO ROMANO", "ARSOLI", "ARTENA", "BELLEGRA",
    "CAMERATA NUOVA", "CANTERANO", "CAPRANICA PRENESTINA", "CARPINETO ROMANO", "CASAPE", 
    "CASTEL SAN PIETRO ROMANO", "CASTEL MADAMA", "CAVE", "CERRETO LAZIALE", "CERVARA DI ROMA", 
    "CICILIANO", "CINETO ROMANO", "COLLEFERRO", "FONTE NUOVA", "GALLICANO NEL LAZIO", "GAVIGNANO",
    "GENAZZANO", "GERANO", "GORGA", "GUIDONIA MONTECELIO", "JENNE", "LABICO", "LICENZA", 
    "MANDELA", "MARANO EQUO", "MARCELLINA", "MENTANA", "MONTEFLAVIO", "MONTELANICO", 
    "MONTELIBRETTI", "MONTEROTONDO", "MONTORIO ROMANO", "MORICONE", "NEROLA", "OLEVANO ROMANO",
    "PALESTRINA", "PALOMBARA SABINA", "PERCILE", "PISONIANO", "POLI", "RIOFREDDO", 
    "ROCCA CANTERANO", "ROCCA DI CAVE", "ROCCA SANTO STEFANO", "ROCCAGIOVINE", "ROIATE", 
    "ROVIANO", "SAMBUCI", "SAN CESAREO", "SAN GREGORIO DA SASSOLA", "SAN POLO DEI CAVALIERI", 
    "SAN VITO ROMANO", "SARACINESCO", "SANT'ANGELO ROMANO", "SEGNI", "SUBIACO", "TIVOLI", "VALLEPIETRA", 
    "VALLINFREDA", "VALMONTONE", "VICOVARO", "VIVARO ROMANO", "ZAGAROLO"
]

asl_rm_h = [
    "ALBANO LAZIALE", "ANZIO", "ARDEA", "ARICCIA", "CASTEL GANDOLFO", "CIAMPINO", "COLONNA", 
    "FRASCATI", "GENZANO DI ROMA", "GROTTAFERRATA", "LANUVIO", "LARIANO", "MARINO", 
    "MONTE PORZIO CATONE", "MONTE COMPATRI", "NEMI", "NETTUNO", "POMEZIA", "ROCCA DI PAPA", 
    "ROCCA PRIORA", "VELLETRI"
]

elementi = 0

# === Funzione per calcolare distanza reale ===
def get_real_distance(origin_latlon, destination_str):

    global elementi

    key = f"{origin_latlon}-{destination_str}"
    if key in distance_cache:
        return distance_cache[key]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_latlon[0]},{origin_latlon[1]}",
        "destinations": destination_str,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving"
    }

    elementi = elementi + 1

    return

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("rows") and data["rows"][0]["elements"][0]["status"] == "OK":
        distanza = data["rows"][0]["elements"][0]["distance"]["value"]
        durata = data["rows"][0]["elements"][0]["duration"]["value"]
        distance_cache[key] = {"distanza": distanza, "durata": durata}
        with open(CACHE_FILE, "w") as f:
            json.dump(distance_cache, f, indent=4)
        return {"distanza": distanza, "durata": durata}

    print(f"⚠️ Errore API per {destination_str}")
    return {"distanza": float("inf"), "durata": float("inf")}

# === Inizio Elaborazione ===
output = {}

for feature in nuclei_data["features"]:
    props = feature["properties"]
    loc_id = str(int(props["LOC21_ID"]))
    pro_com = props["PRO_COM"]
    cod_uts = props["COD_UTS"]

    nome_comune = nome_comuni_dict.get(pro_com)
    if not nome_comune:
        continue

    # Filtro popolazione
    if popolazione_dict.get(nome_comune) is None or popolazione_dict[nome_comune] >= 40000:
        continue

    # Centroide del nucleo urbano
    easting, northing = feature["geometry"]["coordinates"]
    centroide = convert_utm_to_wgs84(easting, northing)

    # Verifica se il comune ha ospedale assegnato
    ospedali_associati = ospedali_comuni.get(nome_comune, [])

    if ospedali_associati:
        min_dist = float("inf")
        best_osp = None
        best_durata = None

        for osp_id in ospedali_associati:
            osp_row = df_ospedali[df_ospedali['Id_struttura'] == osp_id].iloc[0]
            destination_str = f"{osp_row['nome_struttura']}, {osp_row['comune']}, {osp_row['provincia']}"
            dist_info = get_real_distance(centroide, destination_str)

            continue

            if dist_info["distanza"] < min_dist:
                min_dist = dist_info["distanza"]
                best_durata = dist_info["durata"]
                best_osp = osp_id

    else:
        # Logica ASL/Provincia
        if cod_uts == 258:
            asl_comune = asl_roma_dict.get(nome_comune)
            if not asl_comune:
                continue
            ospedali_zona = df_ospedali[df_ospedali['ASL'] == asl_comune]
        else:
            match cod_uts:
                case 56: prov = "VT"
                case 57: prov = "RI"
                case 59: prov = "LT"
                case 60: prov = "FR"
                case _: continue
            ospedali_zona = df_ospedali[df_ospedali['provincia'] == prov]

        min_dist = float("inf")
        best_osp = None
        best_durata = None

        for _, osp in ospedali_zona.iterrows():
            destination_str = f"{osp['nome_struttura']}, {osp['comune']}, {osp['provincia']}"
            dist_info = get_real_distance(centroide, destination_str)

            continue

            if dist_info["distanza"] < min_dist:
                min_dist = dist_info["distanza"]
                best_durata = dist_info["durata"]
                best_osp = osp['Id_struttura']

    if best_osp:
        if nome_comune not in output:
            output[nome_comune] = {}
        output[nome_comune][loc_id] = {
            "ospedale_id": best_osp,
            "distanza_m": min_dist,
            "durata_s": best_durata
        }
        print(f"✅ Nucleo {loc_id} - Comune {nome_comune} ➜ Ospedale {best_osp}")

# === Salvataggio Output ===
with open("hospitals_by_urban_centers.json", "w") as f:
    json.dump(output, f, indent=4)

print("🎉 Completato! Output salvato. - elementi: ", str(elementi))
