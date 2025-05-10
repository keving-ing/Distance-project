import pandas as pd
import numpy as np

# === File paths ===
INPUT_FILE = "aggregated_ps_distances_weighted.csv"
OUTPUT_FILE = "aggregated_ps_by_municipality.csv"
OUTPUT_EXCEL_FILE = "aggregated_ps_by_municipality.xlsx"

# === Loading data ===
df = pd.read_csv(INPUT_FILE)

df['Comune'] = df['Comune'].astype(str)
df['Nucleo_ID'] = df['Nucleo_ID'].astype(str)
df['Popolazione'] = df['Popolazione'].astype(float)

# === Metrics to calculate ===
metriche = ["mean_km", "mean_min"]

# === Calculation of total population per municipality based on the population of individual cores ===
comune_peso = df.groupby('Comune')['Popolazione'].sum().reset_index()
comune_peso.rename(columns={'Popolazione': 'Popolazione_totale'}, inplace=True)

# === Weighted averaging fFunction ===
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

# === Aggregation by municipality ===
df_aggregato = df.groupby('Comune').apply(weighted_metrics).reset_index()

# === Standard deviation calculation ===
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

# === Final merge ===
df_finale = pd.merge(comune_peso, df_aggregato, on="Comune", how="left")
df_finale = pd.merge(df_finale, df_std, on="Comune", how="left")

# === Saving output ===
df_finale.to_csv(OUTPUT_FILE, index=False)
df_finale.to_excel(OUTPUT_EXCEL_FILE, index=False, sheet_name="Ps_Aggregated")

print(f"✅ Aggregated data saved in {OUTPUT_FILE} e {OUTPUT_EXCEL_FILE}")
