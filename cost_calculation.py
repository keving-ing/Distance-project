import json

def count_total_combinations(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_combinations = 0

    for block in data.values():
        num_origins = len(block.get("origin_addresses", []))
        num_destinations = len(block.get("destination_addresses", []))
        total_combinations += num_origins * num_destinations

    print(f"Totale combinazioni origine-destinazione: {total_combinations}")

# Esempio di utilizzo
if __name__ == "__main__":
    json_path = "DATA_DISTANCIAS\google_distances_transit_cache1.json"  # Sostituisci con il nome corretto del file
    count_total_combinations(json_path)