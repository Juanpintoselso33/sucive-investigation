"""
Procesamiento de tipos de cambio históricos
"""
import pandas as pd
from ..utils.io import ensure_dir, read_file
from ..utils.transformations import resample_annual
from ..utils.validations import validate_non_empty, check_required_columns

def process_exchange_rate(input_path, output_path, years_params):
    """Procesa tipos de cambio históricos"""
    print("Procesando tipos de cambio...")
    df = read_file(input_path)
    
    # Validaciones
    validate_non_empty(df, "Tipo de cambio")
    check_required_columns(df, ['Fecha', 'Dólar.USA.Venta'])
    
    # Preparar datos
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%Y')
    df = df.set_index('Fecha')
    
    # Calcular promedio anual del tipo de cambio venta
    tc_annual = resample_annual(df['Dólar.USA.Venta'])
    
    # Obtener TC 2020 para normalización
    tc_2020 = tc_annual[tc_annual.index.year == years_params['base_year']].iloc[0]
    
    # Guardar resultados
    ensure_dir(output_path)
    tc_annual.to_csv(output_path)
    
    return tc_2020, tc_annual