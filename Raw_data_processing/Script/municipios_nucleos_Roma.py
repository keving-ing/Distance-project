import json
import geopandas as gpd

# Caricare il file JSON delle scuole per comune
with open("Raw_data_processing/DATA/hospital_by_municipality_with_nuclei.json", "r", encoding="utf-8") as f:
    school_data = json.load(f)

# Caricare lo shapefile dei comuni (estraiamo anche COD_UTS)
comuni_gdf = gpd.read_file("C:/Users/vehico/Documents/Thesis/comuni.zip")[["PRO_COM", "COMUNE", "COD_UTS"]]

# Filtrare solo i comuni con COD_UTS == 258
comuni_gdf = comuni_gdf[comuni_gdf["COD_UTS"] == 258]

# Caricare lo shapefile dei nuclei urbani (estraiamo PRO_COM e LOC21_ID)
nuclei_gdf = gpd.read_file("C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp")[["PRO_COM", "LOC21_ID"]]

# Creare un dizionario { PRO_COM: [lista di LOC21_ID] }
nuclei_dict = nuclei_gdf.groupby("PRO_COM")["LOC21_ID"].apply(list).to_dict()

# Creare un dizionario { Nome Comune: PRO_COM } solo per i comuni filtrati
comuni_dict = comuni_gdf.set_index(comuni_gdf["COMUNE"].str.upper())["PRO_COM"].to_dict()

# Creare un nuovo dizionario con solo i comuni filtrati e nuclei associati
filtered_school_data = {}

for comune, dati in school_data.items():
    pro_com = comuni_dict.get(comune.upper())
    if pro_com:
        nuclei_urbani = nuclei_dict.get(pro_com, [])
        dati["nuclei"] = nuclei_urbani
        filtered_school_data[comune] = dati

# Salvare il file aggiornato solo con i comuni selezionati
with open("hospital_by_municipality_with_nuclei_ROMA_OK.json", "w", encoding="utf-8") as f:
    json.dump(filtered_school_data, f, indent=4, ensure_ascii=False)

print("✅ File filtrato e aggiornato salvato come 'hospital_by_municipality_with_nuclei_filtered.json'")
