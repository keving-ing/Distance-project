import json
import requests
import pandas as pd
from pyproj import Transformer
import os
import geopandas as gpd
import zipfile
import os

comuni_zip = "C:/Users/vehico/Documents/Thesis/comuni.zip"
comuni_folder = "C:/Users/vehico/Documents/Thesis/comuni"

# Estrazione shapefile
with zipfile.ZipFile(comuni_zip, 'r') as zip_ref:
    zip_ref.extractall(comuni_folder)

comuni_shp_files = [f for f in os.listdir(comuni_folder) if f.endswith(".shp")]
comuni_shp_file = os.path.join(comuni_folder, comuni_shp_files[0]) if comuni_shp_files else None

# Carica comuni
gdf_comuni = gpd.read_file(comuni_shp_file)
gdf_comuni['COMUNE'] = gdf_comuni['COMUNE'].str.upper()

# Dizionario {comune: COD_UTS}
cod_uts_dict = dict(zip(gdf_comuni['COMUNE'], gdf_comuni['COD_UTS']))

# Caricamento dati popolazione
df_popolazione = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv", delimiter=",")
df_popolazione['Territorio'] = df_popolazione['Territorio'].str.upper()

# Creiamo un dizionario {comune: popolazione}
popolazione_dict = dict(zip(df_popolazione['Territorio'], df_popolazione['Value']))

# === Definizione Liste Comuni Provincia di Roma ===

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

# === Creazione Dizionario Comune -> ASL ===
asl_roma_dict = {}
for comune in asl_rm_f:
    asl_roma_dict[comune] = "ASL RM/F"
for comune in asl_rm_g:
    asl_roma_dict[comune] = "ASL RM/G"
for comune in asl_rm_h:
    asl_roma_dict[comune] = "ASL RM/H"


# === CONFIGURAZIONE ===
GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"
CACHE_FILE = "distanze_ospedali_cache.json"


# Trasformatore coordinate UTM -> WGS84
transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

def convert_utm_to_wgs84(easting, northing):
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

# Carica cache distanze
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        try:
            distance_cache = json.load(f)
        except json.JSONDecodeError:
            distance_cache = {}
else:
    distance_cache = {}

elementi = 0 
# Funzione per chiamare Google Distance Matrix API
def get_real_distance(origin_latlon, destination_str):

    global elementi

    key = f"{origin_latlon}-{destination_str}"
    if key in distance_cache:
        print(f"📌 Cache trovata per: {destination_str}")
        return distance_cache[key]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_latlon[0]},{origin_latlon[1]}",
        "destinations": destination_str,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
        "departure_time": 1745485200  # Considera il traffico attuale
    }

    elementi = elementi + 1

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("rows") and data["rows"][0]["elements"][0]["status"] == "OK":
        distanza = data["rows"][0]["elements"][0]["distance"]["value"]  # metri
        distance_cache[key] = distanza
        with open(CACHE_FILE, "w") as f:
            json.dump(distance_cache, f, indent=4)
        return distanza

    print(f"⚠️ Errore per {destination_str}: ", data)
    return float("inf")

# === Caricamento Dati ===
with open("Raw_data_processing/DATA/hospitals_by_municipality.json", "r") as f:
    ospedali_comuni = json.load(f)

with open("C:/Users/vehico/Documents/Thesis/centroidi_comuni.geojson", "r") as f:
    centroidi_data = json.load(f)

df_ospedali = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/elencoospedali.csv")
df_ospedali['comune'] = df_ospedali['comune'].str.upper()


# Dizionario centroidi {comune: (lat, lon)}
centroidi = {}
for feature in centroidi_data["features"]:
    nome_comune = feature["properties"]["COMUNE"].upper()
    easting, northing = feature["geometry"]["coordinates"]
    lat, lon = convert_utm_to_wgs84(easting, northing)
    centroidi[nome_comune] = (lat, lon)


# === Analisi Comuni ===
for comune, ospedali_ids in ospedali_comuni.items():


    

    popolazione = popolazione_dict.get(comune)

    if not popolazione or popolazione > 40000:
        continue  # Salta comuni piccoli

    if ospedali_ids:
        continue  # Comune già servito

    # Ricava la provincia dall'archivio comuni
    provincia_val = gdf_comuni[gdf_comuni['COMUNE'] == comune]['COD_UTS'].values

    if not provincia_val.size:
        print(f"⚠️ Provincia non trovata per {comune}")
        continue

    # Filtra i comuni in provincia di Roma
    if cod_uts_dict.get(comune) == 258:

        asl_comune = asl_roma_dict.get(comune)

        if not asl_comune:
            print(f"⚠️ Comune {comune} della provincia di Roma senza ASL assegnata, salto.")
            continue

        ospedali_provincia = df_ospedali[df_ospedali['ASL'] == asl_comune]
    else:
        provincia_val = gdf_comuni[gdf_comuni['COMUNE'] == comune]['COD_UTS'].values
        if not provincia_val.size:
            print(f"⚠️ Provincia non trovata per {comune}")
            continue

        match provincia_val:
            case 56:
                provincia_val = "VT"
            case 57:
                provincia_val = "RI"
            case 59:
                provincia_val = "LT"
            case 60:
                provincia_val = "FR"

        ospedali_provincia = df_ospedali[df_ospedali['provincia'] == provincia_val]


    centroide = centroidi.get(comune)
    if not centroide:
        print(f"❌ Centroide mancante per {comune}")
        continue


    min_dist = float("inf")
    ospedale_piu_vicino = None

    for _, osp in ospedali_provincia.iterrows():

        destination_str = f"{osp['nome_struttura']}, {osp['comune']}, {osp['provincia']}"
        distanza = get_real_distance(centroide, destination_str)

        if distanza < min_dist:
            min_dist = distanza
            ospedale_piu_vicino = osp['Id_struttura']

    if ospedale_piu_vicino:
        ospedali_comuni[comune] = [ospedale_piu_vicino]
        print(f"🏥 Assegnato ospedale {ospedale_piu_vicino} al comune {comune}")


# === Salvataggio Output ===
with open("hospitals_by_municipality_updated_OK.json", "w") as f:
    json.dump(ospedali_comuni, f, indent=4)

print("✅ File aggiornato e salvato. - elementi: " + str(elementi))
