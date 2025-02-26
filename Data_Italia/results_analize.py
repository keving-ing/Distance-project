import json
import matplotlib.pyplot as plt

# Nome file di input e output
INPUT_FILE = "school_by_municipality_with_distances_complete.json"
OUTPUT_FILE = "filtered_long_distances.json"

# Soglia di distanza (50 km in metri)
DISTANCE_THRESHOLD = 40000

def analyze_distances(input_file, output_file, threshold):
    """
    Analizza il file JSON e filtra i comuni in cui almeno una distanza supera la soglia.
    Mantiene tutto il contenuto del comune nel file di output se almeno una distanza supera il limite.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered_results = {}

    # Estrarre tutte le distanze in km
    all_distances = []
    for comune, comune_data in data.items():
        if "DISTANCE" in comune_data:
            for nucleo, scuole in comune_data["DISTANCE"].items():
                for scuola, details in scuole.items():
                    all_distances.append(details["distanza_m"] / 1000)  # Convertire in km

    # Creare il boxplot per identificare outliers
    plt.figure(figsize=(10, 6))
    plt.boxplot(all_distances, vert=False, patch_artist=True)
    plt.xlabel("Distanza (km)")
    plt.title("Distribuzione delle distanze scuola-nucleo urbano")
    plt.grid(True)
    plt.show()

    for comune, comune_data in data.items():
        # Controlliamo se ci sono distanze
        has_long_distance = False

        if "DISTANCE" in comune_data:
            for nucleo_id, destinations in comune_data["DISTANCE"].items():
                for destination, info in destinations.items():
                    if info["distanza_m"] > threshold:
                        has_long_distance = True
                        break
                if has_long_distance:
                    break

        # Se almeno una distanza supera i 50 km, aggiungiamo il comune intero all'output
        if has_long_distance:
            filtered_results[comune] = comune_data

    # Salvare il nuovo file JSON con i risultati filtrati
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_results, f, indent=4, ensure_ascii=False)

    num_comuni = len(filtered_results)
    print(num_comuni)

    print(f"✅ File '{output_file}' salvato con comuni che hanno almeno una distanza > {threshold / 1000} km.")

    

# **Esegui lo script**
analyze_distances(INPUT_FILE, OUTPUT_FILE, DISTANCE_THRESHOLD)
