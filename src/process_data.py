# Importaciones actualizadas
import os
import pandas as pd
import geopandas as gpd
from utils.io import ensure_dir, read_file
from utils.transformations import (
    to_constant_prices,
    normalize_to_base_year,
    resample_annual,
    filter_by_years
)
from processors.economic import process_gdp_deflator, validate_gdp_data
from processors.prices import process_cpi
from processors.taxes import process_vehicle_tax
from processors.fuels import process_gasoline, process_diesel
from processors.geo import process_shapefile

# ---------------------------
# Funciones principales
# ---------------------------

def convert_deflator(file_path):
    """Función obsoleta - Reemplazada por processors.economic.process_gdp_deflator"""
    raise DeprecationWarning("Esta función fue reemplazada por processors.economic.process_gdp_deflator")

def process_ipc(input_path, output_path, years_params):
    """Función obsoleta - Reemplazada por processors.prices.process_cpi"""
    raise DeprecationWarning("Esta función fue reemplazada por processors.prices.process_cpi")

def process_pib(input_pib, input_deflator, output_path, years_params):
    """Función obsoleta - Reemplazada por processors.economic.process_gdp"""
    raise DeprecationWarning("Esta función fue reemplazada por processors.economic.process_gdp")

def process_patents(input_ingresos, input_ipc, output_path, years_params, exchange_rate):
    """Función obsoleta - Reemplazada por processors.taxes.process_vehicle_tax"""
    raise DeprecationWarning("Esta función fue reemplazada por processors.taxes.process_vehicle_tax")

def process_shapefile(input_dir, output_dir):
    """Función obsoleta - Reemplazada por processors.geo.process_shapefile"""
    raise DeprecationWarning("Esta función fue reemplazada por processors.geo.process_shapefile")

# ---------------------------
# Funciones adicionales (actualizadas)
# ---------------------------

def process_nafta(input_path, output_path, years_params):
    """Procesa datos de ventas de nafta en metros cúbicos
    
    Args:
        input_path: Ruta al archivo de datos crudos
        output_path: Ruta donde guardar los datos procesados
        years_params: Parámetros de años para filtrado
    
    Returns:
        DataFrame con volúmenes anuales de venta de nafta
    """
    return process_gasoline(
        input_path=input_path, 
        output_path=output_path, 
        years_params=years_params,
        ipc_df=None,  # Ya no necesitamos el IPC
        tc_2020=None  # Ya no necesitamos el tipo de cambio
    )

def process_gasoil(input_path, output_path, years_params):
    """Wrapper para processors.fuels.process_diesel"""
    return process_diesel(input_path, output_path, years_params)

def process_participacion_pib(input_path, output_path, years_params):
    """Implementación real usando el nuevo framework"""
    print("Procesando participación del PIB...")
    df = read_file(input_path)
    
    # Validación de datos
    if df.empty:
        raise ValueError("Datos de participación PIB vacíos")
    
    # Procesamiento
    df_processed = (
        df.pipe(filter_by_years, years_params=years_params)
          .pipe(normalize_to_base_year, base_year=2020)
    )
    
    ensure_dir(output_path)
    df_processed.to_csv(output_path, index=False)
    return df_processed

def process_pib_departamental(input_path, output_path, years_params):
    """Implementación real usando el nuevo framework"""
    print("Procesando PIB departamental...")
    
    # Cargar y validar
    df = read_file(input_path)
    required_columns = ['departamento', 'año', 'pib_nominal']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"El dataset debe contener las columnas: {required_columns}")
    
    # Procesamiento
    df_processed = (
        df.pipe(filter_by_years, years_params=years_params)
          .assign(pib_constante=lambda x: to_constant_prices(x, config.data.raw.gdp_deflator.file, years_params))
    )
    
    ensure_dir(output_path)
    df_processed.to_csv(output_path, index=False)
    return df_processed 