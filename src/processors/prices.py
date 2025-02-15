"""
Procesamiento de índices de precios
"""
import pandas as pd
from ..utils.io import ensure_dir, read_file
from ..utils.transformations import resample_annual, normalize_to_base_year

def process_cpi(input_path, output_path, years_params):
    """Procesa el IPC"""
    cpi_df = read_file(input_path, index_col=0, parse_dates=True)
    
    # Procesamiento del IPC
    cpi_annual = resample_annual(cpi_df['cpi_0'])
    cpi_annual = normalize_to_base_year(cpi_annual, base_year=years_params['base_year'])
    
    # Filtrar por años configurados
    cpi_annual = cpi_annual[
        (cpi_annual.index.year >= years_params['start']) &
        (cpi_annual.index.year <= years_params['end'])
    ]
    
    # Renombrar el índice antes de guardar
    cpi_annual.index.name = 'ano'  # Aseguramos que use 'ano' sin tilde
    
    ensure_dir(output_path)
    cpi_annual.to_csv(output_path)
    return cpi_annual 