import json
import pandas as pd
import geopandas as gpd

# === File paths ===
INPUT_FILE = "ps_by_municipality_with_distances.json"
POPULATION_FILE = "C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp"
OUTPUT_FILE = "aggregated_ps_distances_weighted.csv"
OUTPUT_EXCEL_FILE = "aggregated_ps_distances_weighted.xlsx"

# === Loading population data for urban areas ===
gdf = gpd.read_file(POPULATION_FILE)
population_data = gdf.set_index("LOC21_ID")["POP21"].to_dict()

def analyze_hospital_distances_weighted(input_file, output_file, output_excel):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for comune, comune_data in data.items():
        if "DISTANCE" not in comune_data:
            continue

        for nucleo_id, destinations in comune_data["DISTANCE"].items():
            nucleo_id_float = float(nucleo_id)
            pop = population_data.get(nucleo_id_float, 0)

            if pop <= 0:
                continue  # Skip areas with zero or very low population

            distances = []
            durations = []
            weights = []

            for dest, info in destinations.items():
                distances.append(info["distanza_m"] / 1000)  # km
                durations.append(info["tempo_s"] / 60)       # minutes
                weights.append(pop)  # Population weights each entry

            if distances:
                weights_series = pd.Series(weights)
                distances_series = pd.Series(distances)
                durations_series = pd.Series(durations)

                result = {
                    "Comune": comune,
                    "Nucleo_ID": nucleo_id,
                    "Popolazione": pop,
                    "mean_km": (distances_series * weights_series).sum() / weights_series.sum(),
                    "St.Dv_km": distances_series.std(),
                    "mean_min": (durations_series * weights_series).sum() / weights_series.sum(),
                    "St.Dv_min": durations_series.std()
                }
            else:
                result = {
                    "Comune": comune,
                    "Nucleo_ID": nucleo_id,
                    "Popolazione": pop,
                    "mean_km": None,
                    "St.Dv_km": None,
                    "mean_min": None,
                    "St.Dv_min": None
                }

            results.append(result)

    df = pd.DataFrame(results)

    df.to_csv(output_file, index=False, encoding="utf-8")
    df.to_excel(output_excel, index=False, sheet_name="Hospital Distances")

    print(f"✅ File '{output_file}' saved with weighted statistics on hospital distances.")

# === Execute Aggregation ===
analyze_hospital_distances_weighted(INPUT_FILE, OUTPUT_FILE, OUTPUT_EXCEL_FILE)
