# Re-import after code state reset
import pandas as pd
import os
import json
import zipfile
import geopandas as gpd
import re

# === Percorsi dei file ===
medici_folder = ""
comuni_zip = "C:/Users/vehico/Documents/Thesis/comuni.zip"
comuni_folder = "C:/Users/vehico/Documents/Thesis/comuni"
output_json = "medici_by_municipality_noDuplicati.json"

# Estrai lo shapefile dei comuni se non già estratto
if not os.path.exists(comuni_folder):
    os.makedirs(comuni_folder)
    with zipfile.ZipFile(comuni_zip, 'r') as zip_ref:
        zip_ref.extractall(comuni_folder)

# Carica lo shapefile dei comuni del Lazio
shp_files = [f for f in os.listdir(comuni_folder) if f.endswith(".shp")]
if not shp_files:
    raise FileNotFoundError("Shapefile dei comuni non trovato nella cartella specificata.")
shp_path = os.path.join(comuni_folder, shp_files[0])
gdf_comuni = gpd.read_file(shp_path)
gdf_comuni_lazio = gdf_comuni[gdf_comuni['COD_REG'] == 12].copy()
gdf_comuni_lazio['COMUNE'] = gdf_comuni_lazio['COMUNE'].str.upper()

# === Carica file popolazione ===
popolazione_df = pd.read_csv("Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv")

# Mantieni solo colonne utili e rinomina
popolazione_df = popolazione_df[['ITTER107', 'Value']]
popolazione_df.rename(columns={'ITTER107': 'COD_COM', 'Value': 'Popolazione'}, inplace=True)

# Converti codice a stringa per matchare con shapefile
popolazione_df['COD_COM'] = popolazione_df['COD_COM'].astype(str)


# Aggiungi popolazione al GeoDataFrame dei comuni
gdf_comuni_lazio['PRO_COM'] = gdf_comuni_lazio['PRO_COM'].astype(str)

gdf_comuni_lazio = gdf_comuni_lazio.merge(
    popolazione_df,
    left_on='PRO_COM',
    right_on='COD_COM',
    how='left'
)


# Crea lista dei comuni sotto soglia (≤ 40.000)
comuni_sotto_soglia = gdf_comuni_lazio[gdf_comuni_lazio['Popolazione'] <= 40000]['COMUNE'].tolist()

comuni_lista = sorted(comuni_sotto_soglia)


# Inizializza il dizionario finale
medici_per_comune = {comune: [] for comune in comuni_lista}

# Funzione per estrarre il comune dall'indirizzo
def estrai_comune_da_indirizzo(indirizzo, comuni):
    indirizzo = indirizzo.upper()
    for comune in comuni:
        if comune in indirizzo:
            return comune
    return None

# Elenco dei file CSV dei medici
csv_files = [
    "medici_asl_viterbo_noDuplicati.csv",
    "medici_asl_roma6_noDuplicati.csv",
    "medici_asl_roma5_noDuplicati.csv",
    "medici_asl_roma4_noDuplicati.csv",
    "medici_asl_latina_noDuplicati.csv",
    "medici_asl_rieti_noDuplicati.csv",
    "medici_asl_frosinone_noDuplicati.csv"
]

# Processa ciascun file CSV
for csv_file in csv_files:
    file_path = os.path.join(medici_folder, csv_file)
    if not os.path.exists(file_path):
        print(f"File non trovato: {file_path}")
        continue
    df = pd.read_csv(file_path)

    # Determina il nome del file per gestire i formati specifici
    file_name = os.path.basename(csv_file).lower()

   
    df['Indirizzo'] = df['Indirizzo'].astype(str)
    for _, row in df.iterrows():
        indirizzo = row['Indirizzo']
        comune = estrai_comune_da_indirizzo(indirizzo, comuni_lista)
        if comune:
            medici_per_comune[comune].append(indirizzo)
        else:
            print(f"Comune non trovato nell'indirizzo: {indirizzo}")

# Salva il dizionario in formato JSON
with open(output_json, 'w', encoding='utf-8') as json_file:
    json.dump(medici_per_comune, json_file, ensure_ascii=False, indent=4)

print(f"File JSON creato: {output_json}")

# === Statistiche finali ===
comuni_con_indirizzi = {k: v for k, v in medici_per_comune.items() if len(v) > 0}
comuni_senza_indirizzi = {k: v for k, v in medici_per_comune.items() if len(v) == 0}

num_comuni = len(medici_per_comune)
num_con = len(comuni_con_indirizzi)
num_senza = len(comuni_senza_indirizzi)
indirizzi_per_comune = [len(v) for v in comuni_con_indirizzi.values()]
media = sum(indirizzi_per_comune) / num_con if num_con else 0
massimo = max(indirizzi_per_comune) if indirizzi_per_comune else 0
minimo = min(indirizzi_per_comune) if indirizzi_per_comune else 0

# Comuni con più indirizzi (top 10)
top_comuni = sorted(comuni_con_indirizzi.items(), key=lambda x: len(x[1]), reverse=True)[:10]

# Stampa
print("\n📊 STATISTICHE FINALI 📊")
print(f"Totale comuni nel Lazio: {num_comuni}")
print(f"Comuni con almeno un indirizzo: {num_con}")
print(f"Comuni senza indirizzi: {num_senza}")
print(f"Media indirizzi per comune (tra quelli con almeno uno): {media:.2f}")
print(f"Massimo indirizzi in un comune: {massimo}")
print(f"Minimo indirizzi (diverso da zero): {minimo}")

print("\n🏆 Top 10 comuni con più indirizzi:")
for comune, indirizzi in top_comuni:
    print(f" - {comune}: {len(indirizzi)} indirizzi")
