"""
Procesamiento de datos de combustibles
"""
from ..utils.io import ensure_dir, read_file
from ..utils.transformations import filter_by_years, normalize_to_base_year
from ..utils.validations import validate_non_empty, check_required_columns
import os
import yaml
import pandas as pd

def process_fuel(input_path, output_path, years_params, ipc_df, tc_2020, fuel_type="nafta"):
    """Procesa datos de ventas de combustibles en metros cúbicos"""
    print(f"\nProcesando datos de ventas de {fuel_type}...")
    
    # Leer el archivo saltando las filas de metadatos
    df = pd.read_csv(input_path)
    print(f"Shape del DataFrame original: {df.shape}")
    print("\nPrimeras filas del archivo original:")
    print(df.head(10))
    
    # Extraer las fechas y datos numéricos, saltando las filas de metadata
    data_df = df.iloc[9:].copy()
    fechas = pd.to_datetime(data_df.iloc[:, 0])
    print(f"\nCantidad de fechas extraídas: {len(fechas)}")
    print(f"Rango de fechas: {fechas.min()} a {fechas.max()}")
    
    # Limpiar y convertir volúmenes (columna Total)
    volumenes = pd.to_numeric(data_df['Total'].str.strip().str.replace(',', '.'), errors='coerce')
    
    print("\nPrimeras filas de volúmenes:")
    print(volumenes.head())
    print("\nEstadísticas de volúmenes:")
    print(volumenes.describe())
    
    # Crear DataFrame final con fecha
    df_final = pd.DataFrame({
        'fecha': fechas,
        'volumen': volumenes,
        'year': fechas.dt.year
    })
    
    # Agrupar por año y calcular promedio, manteniendo la fecha
    df_anual = df_final.groupby('year').agg({
        'volumen': 'sum',  # Cambiamos a suma para obtener el total anual
        'fecha': 'last'  # Tomamos la última fecha de cada año
    }).reset_index()
    
    df_anual['year'] = df_anual['year'].astype(int)
    
    # Filtrar años según configuración
    df_anual = df_anual[
        (df_anual['year'] >= years_params['start']) & 
        (df_anual['year'] <= years_params['end'])
    ]
    
    print("\nVolúmenes anuales:")
    print(df_anual)
    
    # Guardar resultados
    ensure_dir(os.path.dirname(output_path))
    df_anual.to_csv(output_path, index=False)
    
    # Guardar metadata en YAML
    metadata = {
        'dataset': {
            'name': f'Ventas de {fuel_type}',
            'temporal_coverage': {
                'start': years_params['start'],
                'end': years_params['end'],
                'frequency': 'mensual'
            },
            'unidad': 'metros cúbicos',
            'fuente': 'ANCAP',
            'notas': [
                'Volúmenes mensuales agregados a nivel anual',
                'Incluye ventas totales en el mercado interno',
                'Datos en metros cúbicos'
            ]
        }
    }
    
    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    
    return df_anual, metadata

def process_gasoline(input_path, output_path, years_params, ipc_df, tc_2020):
    """Procesa datos de ventas de nafta en metros cúbicos"""
    return process_fuel(input_path, output_path, years_params, ipc_df, tc_2020, "nafta")

def process_diesel(input_path, output_path, years_params, ipc_df, tc_2020):
    """Procesa datos de ventas de gasoil en metros cúbicos"""
    return process_fuel(input_path, output_path, years_params, ipc_df, tc_2020, "gasoil") 