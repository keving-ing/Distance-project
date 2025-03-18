import pandas as pd
import numpy as np

# Percorsi file
FILE_AUTO = "aggregati_municipio.csv"
FILE_TRANSIT = "aggregati_municipio_transit.csv"
OUTPUT_FILE = "aggregati_avg_driving_transit.csv"

# Caricare i dataset
df_auto = pd.read_csv(FILE_AUTO)
df_transit = pd.read_csv(FILE_TRANSIT)

# Merge dei due dataset sulla colonna "Comune"
df_merged = pd.merge(df_auto, df_transit, on="Comune", suffixes=("_auto", "_transit"))

# Definire le colonne delle metriche
categorie = ["SI", "SP", "SS", "IC"]
metriche_km = [f"{cat}_mean_km" for cat in categorie]
metriche_min = [f"{cat}_mean_min" for cat in categorie]
std_km = [f"{cat}_St.Dv_km" for cat in categorie]
std_min = [f"{cat}_St.Dv_min" for cat in categorie]

# Creare nuovo DataFrame con i valori mediati
df_final = pd.DataFrame()
df_final["Comune"] = df_merged["Comune"]

# Usare la popolazione totale dalla versione "auto" (dovrebbe essere uguale)
df_final["Popolazione_totale"] = df_merged["Popolazione_totale_auto"]

# Calcolare la media tra auto e transit per distanze e tempi
for col in metriche_km + metriche_min:
    df_final[col] = df_merged[[f"{col}_auto", f"{col}_transit"]].mean(axis=1)

# Calcolare la deviazione standard combinata
for col in std_km + std_min:
    sigma1 = df_merged[f"{col}_auto"]
    sigma2 = df_merged[f"{col}_transit"]
    df_final[col] = np.sqrt((sigma1**2 + sigma2**2) / 2)

# Salvare il risultato
df_final.to_csv(OUTPUT_FILE, index=False)
df_final.to_excel("aggregati_municipio_medi.xlsx", index=False, sheet_name="Media_auto_transit")

print(f"✅ File '{OUTPUT_FILE}' salvato con la deviazione standard combinata.")
