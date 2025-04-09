import pandas as pd

# Dati forniti
data = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])

# Filtra i comuni con più di 50000 abitanti
filtered_codes = data[data["Value"] > 40000]["ITTER107"].astype(str).tolist()

print("N. municipality: " + str(len(filtered_codes)))

# Concatena i codici separati da una virgola
result = ",".join(filtered_codes)

# Stampa il risultato
print(result)
