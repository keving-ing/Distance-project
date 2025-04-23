import pandas as pd
import json
import zipfile
import os

# Percorsi file
ospedali_csv = "C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/elencoospedali.csv"
comuni_zip = "C:/Users/vehico/Documents/Thesis/comuni.zip"
comuni_folder = "C:/Users/vehico/Documents/Thesis/comuni"

# Estrazione shapefile comuni (se serve)
with zipfile.ZipFile(comuni_zip, 'r') as zip_ref:
    zip_ref.extractall(comuni_folder)

# Caricamento comuni (GeoDataFrame)
import geopandas as gpd
comuni_shp_files = [f for f in os.listdir(comuni_folder) if f.endswith(".shp")]
comuni_shp_file = os.path.join(comuni_folder, comuni_shp_files[0]) if comuni_shp_files else None

if comuni_shp_file:
    gdf_comuni = gpd.read_file(comuni_shp_file)
    gdf_comuni_lazio = gdf_comuni[gdf_comuni['COD_REG'] == 12].copy()
    gdf_comuni_lazio['COMUNE'] = gdf_comuni_lazio['COMUNE'].str.upper()
    comuni_lista = gdf_comuni_lazio[['COMUNE']].drop_duplicates()

# Caricamento dati ospedali
df_ospedali = pd.read_csv(ospedali_csv)
df_ospedali['comune'] = df_ospedali['comune'].str.upper()

# Dizionario finale: comuni -> lista di ID ospedali
ospedali_per_comune = {}

for _, comune in comuni_lista.iterrows():
    nome_comune = comune['COMUNE']
    ospedali_comune = df_ospedali[df_ospedali['comune'] == nome_comune]['Id_struttura'].tolist()
    ospedali_per_comune[nome_comune] = ospedali_comune

# Salvataggio in JSON
json_file_path = "Raw_data_processing/DATA/hospitals_by_municipality.json"

with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(ospedali_per_comune, json_file, ensure_ascii=False, indent=4)

print(f"File JSON creato: {json_file_path}")
