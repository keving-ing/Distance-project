import json
import geopandas as gpd

# Caricare il file JSON delle scuole per comune
with open("C:/Users/vehico/Documents/Thesis/Distance-project/hospitals_by_municipality_updated_OK.json", "r", encoding="utf-8") as f:
    school_data = json.load(f)

# Caricare lo shapefile dei comuni (estraiamo PRO_COM e nome comune)
comuni_gdf = gpd.read_file("C:/Users/vehico/Documents/Thesis/comuni.zip")[["PRO_COM", "COMUNE"]]

# Caricare lo shapefile dei nuclei urbani (estraiamo PRO_COM e LOC21_ID)
nuclei_gdf = gpd.read_file("C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp")[["PRO_COM", "LOC21_ID"]]

# Creare un dizionario { PRO_COM: [lista di LOC21_ID] }
nuclei_dict = nuclei_gdf.groupby("PRO_COM")["LOC21_ID"].apply(list).to_dict()

# Creare un dizionario { Nome Comune: PRO_COM }
comuni_dict = comuni_gdf.set_index(comuni_gdf["COMUNE"].str.upper())["PRO_COM"].to_dict()


# Aggiungere i nuclei urbani a ogni comune nel file JSON
for comune, ospedali in school_data.items():
    pro_com = comuni_dict.get(comune)
    if pro_com:
        nuclei_urbani = nuclei_dict.get(pro_com, [])
        # Ricostruiamo la struttura come dizionario
        school_data[comune] = {
            "ospedali": ospedali,
            "nuclei": nuclei_urbani
        }


# Salvare il file aggiornato
with open("hospital_by_municipality_with_nuclei.json", "w", encoding="utf-8") as f:
    json.dump(school_data, f, indent=4, ensure_ascii=False)

print("✅ File aggiornato con i nuclei urbani salvato come 'hospital_by_municipality_with_nuclei.json'")
