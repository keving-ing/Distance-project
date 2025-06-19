import pandas as pd
import numpy as np

# Input and output file paths
INPUT_FILE = "C:/Users/vehico/Documents/Thesis/Distance-project/aggregated_school_distances_weighted_Pop_dens.csv"  
OUTPUT_FILE = "aggregati_municipio_density.csv"

df = pd.read_csv(INPUT_FILE)

df['Comune'] = df['Comune'].astype(str)
df['Nucleo_ID'] = df['Nucleo_ID'].astype(str)
df['Densità_popolazione_km2'] = df['Densità_popolazione_km2'].astype(float)

# Definition of categories and types of metrics (km and minutes)
categorie = ["SI", "SP", "SS"]
metriche_norm_km = [f"{cat}_norm_km_density" for cat in categorie]
metriche_norm_min = [f"{cat}_norm_min_density" for cat in categorie]

# Aggregating data by municipality using the normalized values (no weights)
def simple_average(group):
    results = {}

    # Compute the simple average of the normalized values for each category
    for col in metriche_norm_km + metriche_norm_min:
        valori = group[col].dropna()  # Removal of NaN values
        if len(valori) > 0:
            media_semplice = valori.mean()  # Simple average (no weights)
        else:
            media_semplice = np.nan

        results[col] = media_semplice

    return pd.Series(results)

# Aggregating data by municipality (simple average of normalized values)
df_aggregato = df.groupby('Comune').apply(simple_average).reset_index()

# Calculation of the standard deviation for each municipality on the new normalized values
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
df_std = df.groupby('Comune').apply(lambda group: compute_std(group, metriche_norm_km + metriche_norm_min)).reset_index()

# Union of the simple average and final standard deviation
df_finale = df_aggregato.copy()  # Use the aggregated data
df_finale = pd.merge(df_finale, df_std, on="Comune", how="left")

# Printing maximum and minimum values for each category
print("Maximum and minimum values for each category:")
for col in metriche_norm_km + metriche_norm_min:
    max_value = df_finale[col].max()
    min_value = df_finale[col].min()
    print(f"{col}: Max = {max_value}, Min = {min_value}")


# Saving the result in a CSV file
df_finale.to_csv(OUTPUT_FILE, index=False)
df_finale.to_excel("aggregati_municipio_transit_ROMA.xlsx", index=False, sheet_name="Dati_aggregati_municipios")

print(f"Aggregated data saved in {OUTPUT_FILE}")