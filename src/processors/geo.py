"""
Procesamiento de datos geográficos
"""
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from ..utils.io import ensure_dir

def process_shapefile(input_dir, output_dir):
    """Procesa y convierte shapefiles"""
    print("Cargando shapefile...")
    
    # Buscar el primer archivo .shp en el directorio
    shp_files = [f for f in os.listdir(input_dir) if f.endswith('.shp')]
    if not shp_files:
        raise FileNotFoundError(f"No se encontraron archivos .shp en {input_dir}")
    
    # Usar el primer archivo .shp encontrado
    shp_file = shp_files[0]
    print(f"Usando shapefile: {shp_file}")
    
    gdf = gpd.read_file(os.path.join(input_dir, shp_file))
    
    # Simplificar y estandarizar usando los nombres correctos de columnas
    gdf = gdf[['NOMBRE', 'geometry']].rename(columns={'NOMBRE': 'departamento'})
    gdf['departamento'] = gdf['departamento'].str.title()
    
    # Crear directorio de salida completo (no solo el padre)
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar en múltiples formatos
    # Shapefile
    shp_output = os.path.join(output_dir, "uruguay_map.shp")
    gdf.to_file(shp_output)
    
    # GeoJSON
    geojson_output = os.path.join(output_dir, "uruguay_map.geojson")
    gdf.to_file(geojson_output, driver='GeoJSON')
    
    # Visualización
    plt.figure(figsize=(10, 12))
    gdf.plot(edgecolor='black', facecolor='lightgrey')
    plt.title("Departamentos de Uruguay")
    plt.axis("off")
    plt.savefig(os.path.join(output_dir, "mapa_departamentos.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    return gdf

def save_geo_files(gdf, output_dir):
    """Guarda en diferentes formatos geoespaciales"""
    # Shapefile
    shp_path = os.path.join(output_dir, "uruguay_map.shp")
    gdf.to_file(shp_path)
    
    # GeoJSON
    geojson_path = os.path.join(output_dir, "uruguay_map.geojson")
    gdf.to_file(geojson_path, driver='GeoJSON')
    
    # Visualización
    plot_path = os.path.join(output_dir, "mapa_departamentos.png")
    generate_map_plot(gdf, plot_path)

def generate_map_plot(gdf, output_path):
    """Genera visualización del mapa"""
    plt.figure(figsize=(10, 12))
    gdf.plot(edgecolor='black', facecolor='lightgrey')
    plt.title("Departamentos de Uruguay")
    plt.axis("off")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close() 