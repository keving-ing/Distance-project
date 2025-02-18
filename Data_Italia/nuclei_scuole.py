import geopandas as gpd

# Carica i dati
scuole = gpd.read_file("C:/Users/vehico/Documents/Thesis/Distance-project/Data_Italia/geocoded_locations_school.geojson")  # Layer punti
nuclei = gpd.read_file("C:/Users/vehico/Documents/Thesis/nuclei/Località_21/Localita_2021.shp")  # Layer poligoni

# Assicurati che entrambi abbiano lo stesso CRS
scuole = scuole.to_crs(nuclei.crs)

# Effettua lo Spatial Join
scuole_nuclei = gpd.sjoin(scuole, nuclei, how="left", predicate="within")

# Salva il nuovo file con le scuole associate ai nuclei urbani
scuole_nuclei.to_file("scuole_con_nuclei.geojson", driver="GeoJSON")
