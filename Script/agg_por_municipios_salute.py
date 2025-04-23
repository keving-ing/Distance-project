import pandas as pd
import numpy as np

# === Percorsi File ===
INPUT_FILE = "aggregated_hospital_distances_weighted.csv"
OUTPUT_FILE = "aggregated_hospital_by_municipality.csv"
OUTPUT_EXCEL_FILE = "aggregated_hospital_by_municipality.xlsx"

# === Caricamento Dati ===
df = pd.read_csv(INPUT_FILE)

df['Comune'] = df['Comune'].astype(str)
df['Nucleo_ID'] = df['Nucleo_ID'].astype(str)
df['Popolazione'] = df['Popolazione'].astype(float)

# === Metriche da Calcolare ===
metriche = ["mean_km", "mean_min"]

# === Calcolo Popolazione Totale per Comune ===
comune_peso = df.groupby('Comune')['Popolazione'].sum().reset_index()
comune_peso.rename(columns={'Popolazione': 'Popolazione_totale'}, inplace=True)

# === Funzione per Media Ponderata ===
def weighted_metrics(group):
    popolazione = group['Popolazione']
    results = {}

    for col in metriche:
        valori = group[col].dropna()
        pesi = popolazione.loc[valori.index]
        
        if len(valori) > 0:
            media_ponderata = np.average(valori, weights=pesi)
        else:
            media_ponderata = np.nan

        results[col] = media_ponderata

    return pd.Series(results)

# === Aggregazione per Comune ===
df_aggregato = df.groupby('Comune').apply(weighted_metrics).reset_index()

# === Calcolo Deviazione Standard ===
def compute_std(group, metriche):
    results = {}
    for col in metriche:
        valori = group[col].dropna()
        if len(valori) > 1:
            results[f"{col.replace('mean', 'St.Dv')}"] = valori.std()
        else:
            results[f"{col.replace('mean', 'St.Dv')}"] = np.nan
    return pd.Series(results)

df_std = df.groupby('Comune').apply(lambda group: compute_std(group, metriche)).reset_index()

# === Merge Finale ===
df_finale = pd.merge(comune_peso, df_aggregato, on="Comune", how="left")
df_finale = pd.merge(df_finale, df_std, on="Comune", how="left")

# === Salvataggio Output ===
df_finale.to_csv(OUTPUT_FILE, index=False)
df_finale.to_excel(OUTPUT_EXCEL_FILE, index=False, sheet_name="Hospitals_Aggregated")

print(f"✅ Dati aggregati salvati in {OUTPUT_FILE} e {OUTPUT_EXCEL_FILE}")
