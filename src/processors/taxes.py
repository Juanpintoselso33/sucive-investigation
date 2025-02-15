"""
Procesamiento de datos tributarios (patentes vehiculares)
"""
import pandas as pd
from ..utils.io import ensure_dir, read_file
from ..utils.transformations import normalize_to_base_year
import os
import yaml

def process_vehicle_tax(input_path, ipc_path, output_path, years_params, exchange_rate):
    """Procesa datos de patentes vehiculares"""
    print("Cargando datos de patentes...")
    df = read_file(input_path)
    ipc_df = read_file(ipc_path, index_col='ano')
    
    # Procesar datos
    filtered = filter_vehicle_tax(df)
    grouped = group_by_department(filtered, years_params)
    converted = convert_to_constant_usd(grouped, ipc_df, exchange_rate)
    
    # Crear metadata básica
    metadata = {
        'dataset': {
            'name': 'Recaudación de patentes vehiculares',
            'temporal_coverage': {
                'start': years_params['start'],
                'end': years_params['end'],
                'frequency': 'anual'
            },
            'unidad': f'USD constantes {years_params["base_year"]}',
            'fuente': 'OPP Uruguay',
            'notas': [
                f'Tipo de cambio {years_params["base_year"]}: {float(exchange_rate):.2f}',
                'Solo incluye patentes de rodados',
                'Valores deflactados por IPC'
            ]
        }
    }
    
    # Guardar resultados y metadata
    ensure_dir(output_path)
    converted.to_csv(output_path, index=False)
    
    # Guardar metadata en YAML
    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    
    return converted, metadata

def filter_vehicle_tax(df):
    """Filtra y limpia datos de patentes vehiculares"""
    # Asegurar que AÑO sea numérico (si ya lo es, no hace nada)
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    
    # Filtrar solo patentes de rodados
    filtered = df[
        (df['OBJETO'] == 'Sobre Vehiculos') & 
        (df['RUBRO'] == 'Patente de Rodados')
    ].copy()
    
    # Filtrar filas con valores válidos
    filtered = filtered[
        filtered['RECAUDADO'].notna() & 
        filtered['AÑO'].notna() & 
        filtered['DEPARTAMENTO'].notna()
    ]
    
    return filtered

def group_by_department(df, years_params):
    """Agrupa por departamento y año"""
    grouped = df.groupby(['AÑO', 'DEPARTAMENTO'])['RECAUDADO'].sum().reset_index()
    
    # Filtrar por años configurados
    grouped = grouped[
        (grouped['AÑO'] >= years_params['start']) & 
        (grouped['AÑO'] <= years_params['end'])
    ]
    
    return grouped

def convert_to_constant_usd(df, ipc_df, tc_2020):
    """Convierte a USD constantes usando IPC y tipo de cambio 2020"""
    # Convertir el índice del IPC a año
    ipc_df.index = pd.to_datetime(ipc_df.index).year
    
    print(f"\nÍndice IPC después de conversión: {ipc_df.index.tolist()}")
    print(f"Años en df: {df['AÑO'].unique().tolist()}")
    
    df['RECAUDADO'] = df.apply(
        lambda x: (x['RECAUDADO'] * 100 / ipc_df.loc[x['AÑO']]) / tc_2020,
        axis=1
    )
    return df.pivot(index='DEPARTAMENTO', columns='AÑO', values='RECAUDADO').reset_index() 