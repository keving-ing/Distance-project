import json
import pandas as pd
import geopandas as gpd

# Nome file di input e output
INPUT_FILE = "C:/Users/vehico/Documents/Thesis/Distance-project/school_by_municipality_with_distances_complete.json"
POPULATION_FILE = "C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp"
OUTPUT_FILE = "aggregated_school_distances_weighted.csv"
OUTPUT_EXCEL_FILE = "aggregated_school_distances_by_type_weighted.xlsx"

# Definiamo le categorie scolastiche
SCHOOL_CATEGORIES = {
    "SCUOLA INFANZIA": "SI",
    "SCUOLA PRIMARIA": "SP",
    "SCUOLA PRIMO GRADO": "SS",
    "ISTITUTO COMPRENSIVO": "IC",
}

# Caricare la popolazione dei nuclei urbani dal file shapefile
gdf = gpd.read_file(POPULATION_FILE)
population_data = gdf.set_index("LOC21_ID")["POP21"].to_dict()  # Assumiamo che 'LOC21_ID' sia l'ID e 'POP21' la popolazione

print("Chiavi disponibili in population_data:", list(population_data.keys())[:10])  # Mostra le prime 10 chiavi


def analyze_distances_by_type_weighted(input_file, output_file, output_excel):
    """
    Calcola la media ponderata e la deviazione standard delle distanze e dei tempi per ogni nucleo urbano, 
    utilizzando la popolazione come peso.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for comune, comune_data in data.items():
        if "DISTANCE" not in comune_data:
            continue
            
        
        # Creiamo un dizionario per raccogliere le scuole di ogni categoria
        categorized_schools = {cat: set() for cat in SCHOOL_CATEGORIES.values()}
        
        for school_type, category in SCHOOL_CATEGORIES.items():
            if school_type in comune_data:
                categorized_schools[category].update(
                    {(s["LAT"], s["LONG"]) for s in comune_data[school_type]}
                )

        for nucleo_id, destinations in comune_data["DISTANCE"].items():
            nucleo_id = float(nucleo_id)
            if population_data[nucleo_id] <= 20:
                continue  # Skip nuclei senza popolazione

            pop = population_data[nucleo_id]
            school_stats = {
                "Comune": comune,
                "Nucleo_ID": nucleo_id,
                "Popolazione": pop
            }

            # Creiamo un dizionario per raccogliere dati per ogni tipo di scuola
            school_data = {cat: {"distances": [], "durations": [], "weights": []} for cat in SCHOOL_CATEGORIES.values()}

            for destination, info in destinations.items():
                for category, school_set in categorized_schools.items():
                    if destination in {f"{lat},{lon}" for lat, lon in school_set}:  
                        school_data[category]["distances"].append(info["distanza_m"])
                        school_data[category]["durations"].append(info["tempo_s"])
                        school_data[category]["weights"].append(pop)  # Usa la popolazione come peso

            # Calcoliamo media ponderata e deviazione standard per ogni categoria scolastica
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
                else:
                    school_stats[f"{category}_mean_km"] = None
                    school_stats[f"{category}_St.Dv_km"] = None
                    school_stats[f"{category}_mean_min"] = None
                    school_stats[f"{category}_St.Dv_min"] = None

            results.append(school_stats)



    # Creazione DataFrame
    df = pd.DataFrame(results)

    # Salvataggio su CSV
    df.to_csv(output_file, index=False, encoding="utf-8")

    # Salvataggio su Excel
    df.to_excel(output_excel, index=False, sheet_name="Dati aggregati ponderati")

    print(f"✅ File '{output_file}' salvato con le statistiche ponderate delle distanze e tempi medi per ogni tipo di scuola.")

# **Esegui lo script**
analyze_distances_by_type_weighted(INPUT_FILE, OUTPUT_FILE, OUTPUT_EXCEL_FILE)
