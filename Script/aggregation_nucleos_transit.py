import json
import pandas as pd
import geopandas as gpd
from sys import exit 

# Input and output file paths
INPUT_FILE = "C:/Users/vehico/Documents/Thesis/Distance-project/DATA_DISTANCIAS/school_by_municipality_with_distances_complete.json"
INPUT_FILE_TRANSIT = "C:/Users/vehico/Documents/Thesis/Distance-project/DATA_DISTANCIAS/school_by_municipality_with_distances_transit_complete.json"
POPULATION_FILE = "C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp"
OUTPUT_FILE = "aggregated_school_distances_transit_weighted.csv"
OUTPUT_EXCEL_FILE = "aggregated_school_distances_by_transt_weighted.xlsx"

# Definition of categories
SCHOOL_CATEGORIES = {
    "SCUOLA INFANZIA": "SI",
    "SCUOLA PRIMARIA": "SP",
    "SCUOLA PRIMO GRADO": "SS",
}

# Uploadind the population of urban cores from the shapefile
gdf = gpd.read_file(POPULATION_FILE)
population_data = gdf.set_index("LOC21_ID")["POP21"].to_dict()

print("Keys available in population_data:", list(population_data.keys())[:10])


def analyze_distances_by_type_weighted(input_file, input_transit, output_file, output_excel):
    """
    Calculation of the weighted average and standard deviation of distances and times for each urban core, 
    using the population as a weight.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(input_transit, "r", encoding="utf-8") as f:
        data_transit = json.load(f)

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
            if population_data.get(nucleo_id, 0) <= 20:
                continue  # Skip nuclei with no population and population <= 20

            pop = population_data[nucleo_id]
            school_stats = {
                "Comune": comune,
                "Nucleo_ID": nucleo_id,
                "Popolazione": pop
            }

            # Creation of a dictionary to collect data for each type of school
            school_data = {
                                cat: {
                                    "distances": [],
                                    "durations": [],
                                    "weights": [],
                                    "found_count": 0,
                                    "total_count": len(categorized_schools[cat])
                                }
                                for cat in SCHOOL_CATEGORIES.values()
                           }

            for destination, info in destinations.items():
                for category, school_set in categorized_schools.items():
                    if destination in {f"{lat},{lon}" for lat, lon in school_set}:  
                        if comune in data_transit and "DISTANCE" in data_transit[comune]:
                            transit_destinations = data_transit[comune]["DISTANCE"]
                            destination = str(destination)
                            if destination in transit_destinations.get(str(nucleo_id), {}):
                                transit_info = transit_destinations[str(nucleo_id)][destination]
                                distanza_m = transit_info["distanza_m"]
                                tempo_s = transit_info["tempo_s"]
                                
                                school_data[category]["distances"].append(distanza_m)
                                school_data[category]["durations"].append(tempo_s)
                                school_data[category]["weights"].append(pop)
                                school_data[category]["found_count"] += 1
                        else:
                            print("SIAMO ENTRATI QUÀ, manca il comune: " + comune)
                            continue


            # Calculation of weighted mean and standard deviation for each school category
            for category in SCHOOL_CATEGORIES.values():
                if school_data[category]["distances"]:  
                    weights = pd.Series(school_data[category]["weights"])
                    distances = pd.Series(school_data[category]["distances"]) / 1000  # Conversion metres → km
                    durations = pd.Series(school_data[category]["durations"]) / 60  # Convert seconds → minutes

                    school_stats[f"{category}_mean_km"] = (distances * weights).sum() / weights.sum()
                    school_stats[f"{category}_St.Dv_km"] = distances.std()
                    school_stats[f"{category}_mean_min"] = (durations * weights).sum() / weights.sum()
                    school_stats[f"{category}_St.Dv_min"] = durations.std()
                else:
                    school_stats[f"{category}_mean_km"] = None
                    school_stats[f"{category}_St.Dv_km"] = None
                    school_stats[f"{category}_mean_min"] = None
                    school_stats[f"{category}_St.Dv_min"] = None

                school_stats[f"{category}_match_ratio"] = f'{school_data[category]["found_count"]}/{school_data[category]["total_count"]}'
            results.append(school_stats)
            

    df = pd.DataFrame(results)

    # Saving to CSV
    df.to_csv(output_file, index=False, encoding="utf-8")

    # Saving to Excel for better visualization
    df.to_excel(output_excel, index=False, sheet_name="Dati aggregati ponderati")

    print(f"✅ File '{output_file}' saved with weighted statistics of distances and average times for each type of school.")


analyze_distances_by_type_weighted(INPUT_FILE, INPUT_FILE_TRANSIT, OUTPUT_FILE, OUTPUT_EXCEL_FILE)
