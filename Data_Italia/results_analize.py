import json
import matplotlib.pyplot as plt
import seaborn as sns

# Nome file di input e output
INPUT_FILE = "Distance-project\school_by_municipality_with_distances_complete.json"
OUTPUT_FILE = "filtered_long_distances.json"

# Soglia di distanza (40 km in metri)
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

    # Creare un'unica figura con 3 sottografici
    #plt.figure(figsize=(12, 8))

    # 1️⃣ Boxplot
    #plt.subplot(3, 1, 1)
    sns.boxplot(x=all_distances, color="lightblue")
    plt.xlabel("Distanza (km)")
    plt.title("Distribuzione delle distanze scuola-nucleo urbano (Boxplot)")
    plt.grid(True)
    plt.show()

    # 2️⃣ Istogramma
    #plt.subplot(3, 1, 2)
    plt.hist(all_distances, bins=30, color="blue", alpha=0.6, edgecolor="black")
    plt.xlabel("Distanza (km)")
    plt.ylabel("Frequenza")
    plt.title("Istogramma delle distanze scuola-nucleo urbano")
    plt.grid(True)
    plt.show()

    # 3️⃣ Distribuzione KDE
    #plt.subplot(3, 1, 3)
    sns.kdeplot(all_distances, color="red", fill=True, alpha=0.5)
    plt.xlabel("Distanza (km)")
    plt.ylabel("Densità")
    plt.title("Distribuzione della distanza scuola-nucleo urbano (KDE)")
    plt.grid(True)
    plt.show()

    # Mostra i grafici
    #plt.tight_layout()
    

    # Filtrare i comuni con almeno una distanza oltre la soglia
    for comune, comune_data in data.items():
        has_long_distance = False
        if "DISTANCE" in comune_data:
            for nucleo_id, destinations in comune_data["DISTANCE"].items():
                for destination, info in destinations.items():
                    if info["distanza_m"] > threshold:
                        has_long_distance = True
                        break
                if has_long_distance:
                    break

        # Se almeno una distanza supera i 40 km, aggiungiamo il comune all'output
        if has_long_distance:
            filtered_results[comune] = comune_data

    # Salvare il nuovo file JSON con i risultati filtrati
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_results, f, indent=4, ensure_ascii=False)

    num_comuni = len(filtered_results)
    print(f"✅ File '{output_file}' salvato con {num_comuni} comuni che hanno almeno una distanza > {threshold / 1000} km.")

# **Esegui lo script**
analyze_distances(INPUT_FILE, OUTPUT_FILE, DISTANCE_THRESHOLD)
