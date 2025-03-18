import geopandas as gpd
import json

# Caricare il file GeoJSON
gdf = gpd.read_file("C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/confini_nuclei.geojson")

# Creare una nuova colonna per i confinanti
gdf["confinanti"] = None
gdf["confinanti"] = gdf["confinanti"].astype(object)

# Trova i confinanti per ogni comune
for idx, comune in gdf.iterrows():
    confinanti = gdf[gdf.geometry.touches(comune.geometry)]["LOC21_ID"].tolist()
    gdf.at[idx, "confinanti"] = confinanti  # Manteniamo la lista invece di una stringa

# Creare un dizionario con solo Nome Comune e Confinanti
comuni_confinanti = gdf[["LOC21_ID", "confinanti"]].to_dict(orient="records")

# Salvataggio in JSON
output_path = "nuclei_con_confinanti.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(comuni_confinanti, f, ensure_ascii=False, indent=4)

# Restituisco il file JSON generato
output_path
