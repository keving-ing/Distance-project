import json
import pandas as pd
import geopandas as gpd
from sys import exit 

# Nome file di input e output
INPUT_FILE = "C:/Users/vehico/Documents/Thesis/Distance-project/school_by_municipality_with_distances_complete.json"
INPUT_FILE_TRANSIT = "C:/Users/vehico/Documents/Thesis/Distance-project/school_by_municipality_with_distances_transit_complete.json"
POPULATION_FILE = "C:/Users/vehico/Documents/Thesis/geometrias_Lazio.shp"
OUTPUT_FILE = "aggregated_school_distances_transit_weighted.csv"
OUTPUT_EXCEL_FILE = "aggregated_school_distances_by_transt_weighted.xlsx"

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


def analyze_distances_by_type_weighted(input_file, input_transit, output_file, output_excel):
    """
    Calcola la media ponderata e la deviazione standard delle distanze e dei tempi per ogni nucleo urbano, 
    utilizzando la popolazione come peso.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(input_transit, "r", encoding="utf-8") as f:
        data_transit = json.load(f)

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
            if population_data.get(nucleo_id, 0) <= 20:
                continue  # Skip nuclei con popolazione <= 20

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
                        # **PRIMA CERCA IN TRANSIT**, se non trova usa input_file
                        if comune in data_transit and "DISTANCE" in data_transit[comune]:
                            transit_destinations = data_transit[comune]["DISTANCE"]
                            destination = str(destination)
                            #print(transit_destinations)
                            #print(destination)
                            #exit("Errore") 
                            if destination in transit_destinations[str(nucleo_id)]:
                                print("oK")
                                transit_info = transit_destinations[str(nucleo_id)][destination]
                                distanza_m = transit_info["distanza_m"]
                                tempo_s = transit_info["tempo_s"]
                            else:
                                distanza_m = info["distanza_m"]
                                tempo_s = info["tempo_s"]
                        else:
                            distanza_m = info["distanza_m"]
                            tempo_s = info["tempo_s"]

                        # Aggiunge i dati alla categoria corretta
                        school_data[category]["distances"].append(distanza_m)
                        school_data[category]["durations"].append(tempo_s)
                        school_data[category]["weights"].append(pop)

            # Calcoliamo media ponderata e deviazione standard per ogni categoria scolastica
            for category in SCHOOL_CATEGORIES.values():
                if school_data[category]["distances"]:  
                    weights = pd.Series(school_data[category]["weights"])
                    distances = pd.Series(school_data[category]["distances"]) / 1000  # Converti metri → km
                    durations = pd.Series(school_data[category]["durations"]) / 60  # Converti secondi → minuti

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
analyze_distances_by_type_weighted(INPUT_FILE, INPUT_FILE_TRANSIT, OUTPUT_FILE, OUTPUT_EXCEL_FILE)
