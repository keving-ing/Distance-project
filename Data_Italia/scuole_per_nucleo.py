import geopandas as gpd
import json
import zipfile
import os
import math

# File di input
scuole_geojson_file = "C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/geocoded_locations_school.geojson"
nuclei_zip = "C:/Users/vehico/Downloads/Località_21.zip"
nuclei_folder = "C:/Users/vehico/Documents/Thesis/nuclei_urbani"

# # Estrai lo shapefile dei nuclei urbani
# with zipfile.ZipFile(nuclei_zip, 'r') as zip_ref:
#     zip_ref.extractall(nuclei_folder)

# # Identifica il file .shp estratto
# nuclei_shp_files = [f for f in os.listdir(nuclei_folder) if f.endswith(".shp")]

# print(nuclei_shp_files)

nuclei_shp_file = os.path.join("C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp")

print(nuclei_shp_file)

nuclei = 0
scuole = 0

# Carica i dati se il file esiste
if nuclei_shp_file:
    gdf_nuclei = gpd.read_file(nuclei_shp_file)

    # Filtra solo i nuclei urbani del Lazio (TIPO_LOC = 1,2,3,4)
    gdf_nuclei_lazio = gdf_nuclei[(gdf_nuclei['COD_REG'] == 12) & (gdf_nuclei['TIPO_LOC'].isin([1, 2, 3, 4]))].copy()
    
    gdf_nuclei_lazio.loc[:, 'LOC21_ID']

    nuclei_lista = gdf_nuclei_lazio[['LOC21_ID']].drop_duplicates()

    # Carica il dataset delle scuole
    gdf_scuole = gpd.read_file(scuole_geojson_file)

    # Assicurati che entrambi i dataset abbiano lo stesso sistema di riferimento spaziale (CRS)
    if gdf_scuole.crs != gdf_nuclei_lazio.crs:
        gdf_scuole = gdf_scuole.to_crs(gdf_nuclei_lazio.crs)

    # Effettua lo spatial join per associare ogni scuola al nucleo urbano in cui si trova
    gdf_scuole_nucleo = gpd.sjoin(gdf_scuole, gdf_nuclei_lazio, how="left", predicate="within")

    # Categorie di scuole di interesse
    categorie_scuole = ["SCUOLA INFANZIA", "SCUOLA PRIMARIA", "SCUOLA PRIMO GRADO", "ISTITUTO COMPRENSIVO"]

    # Dizionario per memorizzare le scuole per nucleo urbano
    scuole_per_nucleo = {}

    for _, nucleo in nuclei_lista.iterrows():
        nome_nucleo = nucleo['LOC21_ID']
        scuole_per_nucleo[nome_nucleo] = {cat: [] for cat in categorie_scuole}
        nuclei +=1

    for _, scuola in gdf_scuole_nucleo.iterrows():

        nome_nucleo = scuola.get('LOC21_ID', "") # Nome del nucleo urbano
        tipologia = scuola.get("DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA", "")

        if nome_nucleo in scuole_per_nucleo and tipologia in categorie_scuole:
        

            scuola_info = {
                "CODICEISTITUTORIFERIMENTO": scuola.get("CODICEISTITUTORIFERIMENTO"),
                "LAT": scuola.geometry.y,
                "LONG": scuola.geometry.x
            }

            if math.isnan(nome_nucleo):
                print("Errore")

            scuole_per_nucleo[nome_nucleo][tipologia].append(scuola_info)
            scuole += 1

    # Salvataggio dei risultati in formato JSON
    json_file_path = "schools_by_urban_core.json"

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(scuole_per_nucleo, json_file, ensure_ascii=False, indent=4)

    print(f"Dati salvati in: {json_file_path}")

    print(f"Num scuole: {str(scuole)}")
    print(f"Num nuclei: {str(nuclei)}")


