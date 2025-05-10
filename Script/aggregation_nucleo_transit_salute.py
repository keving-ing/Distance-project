import json
import pandas as pd
import geopandas as gpd
import numpy as np

# === File paths ===
INPUT_FILE_TRANSIT = "DATA_DISTANCIAS\medici_by_municipality_with_distances_ROMA.json"
POPULATION_FILE = "C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp"
OUTPUT_FILE = "aggregated_medici_distances_transit_ROMA.csv"
OUTPUT_EXCEL_FILE = "aggregated_medici_distances_transit_ROMA.xlsx"

# === Loading population data for urban areas ===
gdf = gpd.read_file(POPULATION_FILE)
population_data = gdf.set_index("LOC21_ID")[["POP21", "COD_UTS"]].to_dict(orient="index")

def analyze_hospital_distances_transit(input_transit, output_file, output_excel):
    with open(input_transit, "r", encoding="utf-8") as f:
        data_transit = json.load(f)

    results = []

    for comune, comune_data in data_transit.items():
        if "DISTANCE" not in comune_data:
            continue

        for nucleo_id, destinations in comune_data["DISTANCE"].items():
            nucleo_info = population_data.get(float(nucleo_id))
            if not nucleo_info or nucleo_info["POP21"] <= 0 or nucleo_info["COD_UTS"] != 258:
                continue

            pop = nucleo_info["POP21"]

            distances = []
            durations = []
            found_count = 0
            total_count = len(destinations)

            for dest_key, info in destinations.items():
                distanza = info.get("distanza_m")
                tempo = info.get("tempo_s")

                if distanza is not None and tempo is not None:
                    distances.append(distanza / 1000)  # Convert to km
                    durations.append(tempo / 60)       # Convert to minutes
                    found_count += 1

            if distances:
                weights = [pop] * len(distances)  # Equal weights for each destination
                distances_series = pd.Series(distances)
                durations_series = pd.Series(durations)

                result = {
                    "Comune": comune,
                    "Nucleo_ID": nucleo_id,
                    "Popolazione": pop,
                    "mean_km": np.average(distances_series, weights=weights),
                    "St.Dv_km": distances_series.std(),
                    "mean_min": np.average(durations_series, weights=weights),
                    "St.Dv_min": durations_series.std(),
                    "match_ratio": f"{found_count}/{total_count}"
                }
            else:
                result = {
                    "Comune": comune,
                    "Nucleo_ID": nucleo_id,
                    "Popolazione": pop,
                    "mean_km": None,
                    "St.Dv_km": None,
                    "mean_min": None,
                    "St.Dv_min": None,
                    "match_ratio": f"0/{total_count}"
                }

            results.append(result)

    df = pd.DataFrame(results)

    df.to_csv(output_file, index=False, encoding="utf-8")
    df.to_excel(output_excel, index=False, sheet_name="Aggregated_Transit")

    print(f"✅ File '{output_file}' saved with aggregated distances for public transport (Rome).")

# === Execution ===
analyze_hospital_distances_transit(INPUT_FILE_TRANSIT, OUTPUT_FILE, OUTPUT_EXCEL_FILE)
