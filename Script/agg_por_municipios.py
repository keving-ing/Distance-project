import pandas as pd
import numpy as np

# Input and output file paths
INPUT_FILE = "aggregated_school_distances_weighted.csv"  
OUTPUT_FILE = "aggregati_municipio.csv"

df = pd.read_csv(INPUT_FILE)

df['Comune'] = df['Comune'].astype(str)
df['Nucleo_ID'] = df['Nucleo_ID'].astype(str)
df['Popolazione'] = df['Popolazione'].astype(float)

# Definition of categories and types of metrics (km and minutes)
categorie = ["SI", "SP", "SS"]
metriche_km = [f"{cat}_mean_km" for cat in categorie]
metriche_min = [f"{cat}_mean_min" for cat in categorie]

# Calculation of the total population for each municipality
comune_peso = df.groupby('Comune')['Popolazione'].sum().reset_index()
comune_peso.rename(columns={'Popolazione': 'Popolazione_totale'}, inplace=True)

# Calculation of the total population for each municipality
def weighted_metrics(group):
    popolazione = group['Popolazione']
    results = {}

    for col in metriche_km + metriche_min:
        valori = group[col].dropna()  # Removal of NaN values
        pesi = popolazione.loc[valori.index]  # Only takes weights corresponding to valid values
        
        if len(valori) > 0:
            media_ponderata = np.average(valori, weights=pesi)
        else:
            media_ponderata = np.nan

        results[col] = media_ponderata

    return pd.Series(results)

# Aggregating data by municipality
df_aggregato = df.groupby('Comune').apply(weighted_metrics).reset_index()

# Calculation of the standard deviation for each municipality on the new weighted average
def compute_std(group, metriche):
    results = {}
    for col in metriche:
        valori = group[col].dropna()  # Removal of NaN values
        
        if len(valori) > 1:  # Avoid calculating std if there is only one value
            results[f"{col.replace('_mean', '_St.Dv')}"] = valori.std()
        else:
            results[f"{col.replace('_mean', '_St.Dv')}"] = np.nan

    return pd.Series(results)

# Calculation of std municipality by municipality
df_std = df.groupby('Comune').apply(lambda group: compute_std(group, metriche_km + metriche_min)).reset_index()

# Union of weighted mean and final standard deviation
df_finale = pd.merge(comune_peso, df_aggregato, on="Comune", how="left")
df_finale = pd.merge(df_finale, df_std, on="Comune", how="left")

# Saving the result in a CSV file
df_finale.to_csv(OUTPUT_FILE, index=False)
df_finale.to_excel("aggregati_municipio_transit_ROMA.xlsx", index=False, sheet_name="Dati_aggregati_municipios")

print(f"Aggregated data saved in {OUTPUT_FILE}")
