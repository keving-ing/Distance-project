import pandas as pd
import numpy as np

# Percorsi dei file di input e output
INPUT_FILE = "C:/Users/vehico/Documents/Thesis/Distance-project/aggregated_school_distances_transit_weighted.csv"  
OUTPUT_FILE = "aggregati_municipio_transit.csv"

# Caricare il dataset
df = pd.read_csv(INPUT_FILE)

# Assicurarsi che le colonne siano del tipo corretto
df['Comune'] = df['Comune'].astype(str)
df['Nucleo_ID'] = df['Nucleo_ID'].astype(str)
df['Popolazione'] = df['Popolazione'].astype(float)

# Definire le categorie e i tipi di metriche (km e minuti)
categorie = ["SI", "SP", "SS", "IC"]
metriche_km = [f"{cat}_mean_km" for cat in categorie]
metriche_min = [f"{cat}_mean_min" for cat in categorie]

# Calcolare la popolazione totale per ogni Comune
comune_peso = df.groupby('Comune')['Popolazione'].sum().reset_index()
comune_peso.rename(columns={'Popolazione': 'Popolazione_totale'}, inplace=True)

# Funzione per calcolare la media ponderata
def weighted_metrics(group):
    popolazione = group['Popolazione']
    results = {}

    for col in metriche_km + metriche_min:
        valori = group[col].dropna()  # Rimuove valori NaN
        pesi = popolazione.loc[valori.index]  # Prende solo i pesi corrispondenti ai valori validi
        
        if len(valori) > 0:
            media_ponderata = np.average(valori, weights=pesi)
        else:
            media_ponderata = np.nan

        results[col] = media_ponderata

    return pd.Series(results)

# Aggregare i dati per Comune
df_aggregato = df.groupby('Comune').apply(weighted_metrics).reset_index()

# Calcolare la deviazione standard per ogni municipio sulla nuova media ponderata
def compute_std(group, metriche):
    results = {}
    for col in metriche:
        valori = group[col].dropna()  # Rimuove NaN
        
        if len(valori) > 1:  # Evita di calcolare std se c'è un solo valore
            results[f"{col.replace('_mean', '_St.Dv')}"] = valori.std()
        else:
            results[f"{col.replace('_mean', '_St.Dv')}"] = np.nan

    return pd.Series(results)

# Ora calcoliamo la std municipio per municipio
df_std = df.groupby('Comune').apply(lambda group: compute_std(group, metriche_km + metriche_min)).reset_index()

# Unire media ponderata e deviazione standard finale
df_finale = pd.merge(comune_peso, df_aggregato, on="Comune", how="left")
df_finale = pd.merge(df_finale, df_std, on="Comune", how="left")

# Salvare il risultato in un file CSV
df_finale.to_csv(OUTPUT_FILE, index=False)
df_finale.to_excel("aggregati_municipio_transit.xlsx", index=False, sheet_name="Dati_aggregati_municipios")

print(f"Dati aggregati salvati in {OUTPUT_FILE}")
