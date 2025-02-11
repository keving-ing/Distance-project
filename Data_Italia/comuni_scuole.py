import geopandas as gpd
import json
import zipfile
import os

scuole_geojson_file = "scuole.geojson"
comuni_zip = "C:\Users\vehico\Documents\Thesis\comuni.zip"
comuni_folder = "C:\Users\vehico\Documents\Thesis\comuni"
centroidi_comuni = "centroidi_comuni.geojson"

with zipfile.ZipFile(comuni_zip, 'r') as zip_ref:
    zip_ref.extractall(comuni_folder)

comuni_shp_files = [f for f in os.listdir(comuni_folder) if f.endswith(".shp")]
comuni_shp_file = os.path.join(comuni_folder, comuni_shp_files[0]) if comuni_shp_files else None

if comuni_shp_file:
    gdf_comuni = gpd.read_file(comuni_shp_file)

    gdf_comuni_lazio = gdf_comuni[gdf_comuni['COD_REG'] == 12].copy()
    gdf_comuni_lazio.loc[:, 'COMUNE'] = gdf_comuni_lazio['COMUNE'].str.upper()

    comuni_lista = gdf_comuni_lazio[['COMUNE']].drop_duplicates()

    gdf_scuole = gpd.read_file(scuole_geojson_file)

categorie_scuole = ["SCUOLA INFANZIA", "SCUOLA PRIMARIA", "SCUOLA PRIMO GRADO", "ISTITUTO COMPRENSIVO"]

scuole_per_comune = {}

for _, comune in comuni_lista.iterrows():
    nome_comune = comune['COMUNE']
    scuole_per_comune[nome_comune] = {cat: [] for cat in categorie_scuole}

for _, scuola in gdf_scuole.iterrows():
    nome_comune = scuola.get('COMUNE', "").upper()
    tipologia = scuola.get("DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA", "SENZA CATEGORIA")

    if nome_comune in scuole_per_comune and tipologia in categorie_scuole:
        scuola_info = {
            "CODICEISTITUTORIFERIMENTO": scuola.get("CODICEISTITUTORIFERIMENTO"),
            "LAT": scuola.geometry.y,
            "LONG": scuola.geometry.x
        }
        scuole_per_comune[nome_comune][tipologia].append(scuola_info)

for comune, categorie in scuole_per_comune.items():
        
        ha_istituto_comprensivo = len(categorie["ISTITUTO COMPRENSIVO"]) > 0
        ha_infanzia = len(categorie["SCUOLA INFANZIA"]) > 0
        ha_primaria = len(categorie["SCUOLA PRIMARIA"]) > 0
        ha_primo_grado = len(categorie["SCUOLA PRIMO GRADO"]) > 0


        if not ha_istituto_comprensivo:
             if not ha_infanzia:
                  pass
             if not ha_primaria:
                  pass
             if not ha_primo_grado:
                  pass
                  
            
            


json_file_path = "scuole_per_comune_tipologia_completo.json"

with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(scuole_per_comune, json_file, ensure_ascii=False, indent=4)

json_file_path