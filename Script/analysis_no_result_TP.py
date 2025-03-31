import json
import pandas as pd
import re
import geopandas as gpd
from shapely.geometry import Point

# File Paths
log_path = "C:/Users/vehico/Documents/Thesis/distance_matrix_errors.log"
cache_path = "C:/Users/vehico/Documents/Thesis/Distance-project/DATA_DISTANCIAS/google_distances_cache.json"
centroids_paths = "C:/Users/vehico/Documents/centroidi.geojson"

with open(log_path, "r") as f:
    lines = f.readlines()

# Extraction of origin-destination pairs from the log
pattern = re.compile(r"NO RESULT for: ([\d\.\-]+,[\d\.\-]+) - ([\d\.\-]+,[\d\.\-]+)")
coord_pairs = [pattern.findall(line)[0] for line in lines if pattern.search(line)]

with open(cache_path, "r") as f:
    driving_data = json.load(f)

# Function for finding driving distances for a pair
def find_driving_distance(origin, destination, cache):
    for key in cache:
        # Extracts all coordinates from that key
        origins_str, destinations_str = key.split(")-(")
        origins = origins_str.strip("() ").replace("'", "").split(", ")
        destinations = destinations_str.strip("() ").replace("'", "").split(", ")

        # We check whether the co-ordinates are contained in the key
        if origin in origins and destination in destinations:
            origin_index = origins.index(origin)
            dest_index = destinations.index(destination)

            try:
                element = cache[key]["rows"][origin_index]["elements"][dest_index]
                if element["status"] == "OK":
                    return {
                        "distance_m": element["distance"]["value"],
                        "duration_s": element["duration"]["value"]
                    }
            except (IndexError, KeyError):
                continue
    return None

# Apply the search to all pairs
results = []
for origin, destination in coord_pairs:
    res = find_driving_distance(origin, destination, driving_data)
    if res:
        results.append({
            "origin": origin,
            "destination": destination,
            **res
        })
    else:
        results.append({
            "origin": origin,
            "destination": destination,
            "distance_m": None,
            "duration_s": None
        })

# Print and save results

df_results = pd.DataFrame(results)
print(df_results)

centroids_gdf = gpd.read_file(centroids_paths)

# Extraction lat/lon from the column 'origin'
df_results["origin_lat"] = df_results["origin"].apply(lambda x: float(x.split(",")[0]))
df_results["origin_lon"] = df_results["origin"].apply(lambda x: float(x.split(",")[1]))

# Creation of a GeoDataFrame from the origin points (centroids)
geometry = [Point(xy) for xy in zip(df_results["origin_lon"], df_results["origin_lat"])]
gdf_origins = gpd.GeoDataFrame(df_results, geometry=geometry, crs="EPSG:4326")

# Space join
gdf_joined = gpd.sjoin_nearest(
    gdf_origins,
    centroids_gdf[["LOC21_ID", "geometry"]],
    how="left",
    distance_col="dist_meters"
)

unique_ids = gdf_joined["LOC21_ID"].dropna().unique()
unique_ids_str = ",".join(str(int(id_)) for id_ in sorted(unique_ids))
print("LOC21_ID trovati:", unique_ids_str)
print("Numero LOC21_ID trovati:", len(unique_ids))

# Converti di nuovo in DataFrame puro e salva
df_results = pd.DataFrame(gdf_joined.drop(columns="geometry"))
df_results.to_csv("risultati_driving_per_no_result_transit_with_locid.csv", index=False)
