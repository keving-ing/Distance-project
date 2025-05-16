import pandas as pd

# Data provided by the Italian National Institute of Statistics (ISTAT)
data = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Raw_data_processing/Raw_data/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])

# Filter municipalities with more than 40000 inhabitants
filtered_codes = data[data["Value"] > 40000]["ITTER107"].astype(str).tolist()

print("N. municipality: " + str(len(filtered_codes)))

# Concatenate the id codes separated by a comma
result = ",".join(filtered_codes)

# Print result
print(result)
