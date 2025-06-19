import json
import pandas as pd
import geopandas as gpd

# Input and output file paths
INPUT_FILE = "DATA_DISTANCIAS/school_by_municipality_with_distances_complete.json"
POPULATION_FILE = "C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp"
OUTPUT_FILE = "aggregated_school_distances_weighted_Pop_dens.csv"

# Definition of categories
SCHOOL_CATEGORIES = {
    "SCUOLA INFANZIA": "SI",
    "SCUOLA PRIMARIA": "SP",
    "SCUOLA PRIMO GRADO": "SS"
}

# Uploading the population of urban cores from the shapefile
gdf = gpd.read_file(POPULATION_FILE)

# Compute population density per km²
gdf["DENSITY_KM2"] = gdf["POP21"] / (gdf["Shape_Area"] / 1_000_000)

# Create a dictionary with urban core ID and its population density
population_density_data = gdf.set_index("LOC21_ID")["DENSITY_KM2"].to_dict()

print("Keys available in population_data:", list(population_density_data.keys())[:5])


def analyze_distances_by_type_weighted(input_file, output_file):
    """
    Calculation of the weighted average and standard deviation of distances and times for each urban core, 
    using the population as a weight.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for comune, comune_data in data.items():
        if "DISTANCE" not in comune_data:
            continue
            
        
        # Creation of a dictionary to collect the schools in each category
        categorized_schools = {cat: set() for cat in SCHOOL_CATEGORIES.values()}
        
        for school_type, category in SCHOOL_CATEGORIES.items():
            if school_type in comune_data:
                categorized_schools[category].update(
                    {(s["LAT"], s["LONG"]) for s in comune_data[school_type]}
                )

        for nucleo_id, destinations in comune_data["DISTANCE"].items():
            nucleo_id = float(nucleo_id)
            if population_density_data[nucleo_id] <= 20:
                continue  # Skip nuclei with no population and population <= 20

            density = population_density_data.get(nucleo_id)
            school_stats = {
                "Comune": comune,
                "Nucleo_ID": nucleo_id,
                "Densità_popolazione_km2": density
            }

            # Creation of a dictionary to collect data for each type of school
            school_data = {cat: {"distances": [], "durations": [], "weights": []} for cat in SCHOOL_CATEGORIES.values()}

            for destination, info in destinations.items():
                for category, school_set in categorized_schools.items():
                    if destination in {f"{lat},{lon}" for lat, lon in school_set}:  
                        school_data[category]["distances"].append(info["distanza_m"])
                        school_data[category]["durations"].append(info["tempo_s"])
                        school_data[category]["weights"].append(density)  # Use population as weight

            # Calculation of weighted mean and standard deviation for each school category
            for category in SCHOOL_CATEGORIES.values():
                if school_data[category]["distances"]:  
                    weights = pd.Series(school_data[category]["weights"])
                    print(weights)
                    distances = pd.Series(school_data[category]["distances"]) / 1000
                    durations = pd.Series(school_data[category]["durations"]) / 60

                    school_stats[f"{category}_mean_km"] = (distances * weights).sum() / weights.sum()
                    school_stats[f"{category}_St.Dv_km"] = distances.std()
                    school_stats[f"{category}_mean_min"] = (durations * weights).sum() / weights.sum()
                    school_stats[f"{category}_St.Dv_min"] = durations.std()

                    if density > 0:
                        school_stats[f"{category}_norm_km_density"] = school_stats[f"{category}_mean_km"] / density
                        school_stats[f"{category}_norm_min_density"] = school_stats[f"{category}_mean_min"] / density
                    else:
                        school_stats[f"{category}_norm_km_density"] = None
                        school_stats[f"{category}_norm_min_density"] = None
                else:
                    school_stats[f"{category}_mean_km"] = None
                    school_stats[f"{category}_St.Dv_km"] = None
                    school_stats[f"{category}_mean_min"] = None
                    school_stats[f"{category}_St.Dv_min"] = None


            results.append(school_stats)



    df = pd.DataFrame(results)

    # Saving to CSV
    df.to_csv(output_file, index=False, encoding="utf-8")


    print(f"✅ File '{output_file}' saved with weighted statistics of distances and average times for each type of school.")


analyze_distances_by_type_weighted(INPUT_FILE, OUTPUT_FILE)
