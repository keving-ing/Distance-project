import json
import requests
import pandas as pd
import geopandas as gpd
import os
import itertools
import time
from pyproj import Transformer

# Chiave API Google Maps
#GOOGLE_MAPS_API_KEY = "AIzaSyBjj0K6mg5LPe0lwEaAqX3aaBPhMefsR6E"

# File di cache per distanze
CACHE_FILE = "google_distances_cache.json"

# Limiti Distance Matrix API
MAX_ELEMENTS = 100  # nuclei × scuole ≤ 100
MAX_ORIGINS = 25  # massimo 25 nuclei per batch
MAX_DESTINATIONS = 25  # massimo 25 scuole per batch

transformer = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)

# **1️⃣ Caricare il file JSON con scuole e nuclei**
with open("school_by_municipality_with_nuclei.json", "r", encoding="utf-8") as f:
    school_data = json.load(f)

# **2️⃣ Caricare il file con la popolazione e filtrare i comuni < 50.000 abitanti**
pop_df = pd.read_csv("C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/DCIS_POPRES1_12022025124521891.csv", delimiter=",", usecols=["ITTER107", "Territorio", "Value"])
pop_df = pop_df.rename(columns={"ITTER107": "PRO_COM", "Territorio": "Comune", "Value": "Popolazione"})
pop_df["Comune"] = pop_df["Comune"].str.upper()

# Filtrare solo comuni con meno di 50.000 abitanti
filtered_comuni = pop_df[pop_df["Popolazione"] < 50000]["Comune"].tolist()

print(len(filtered_comuni))

filtered_comuni_4 = pop_df[pop_df["Popolazione"] < 35000]["Comune"].tolist()

print(len(filtered_comuni_4))