"""
Procesamiento de variables económicas (PIB, deflactor)
"""
import pandas as pd
from ..utils.io import ensure_dir, read_file
from ..utils.transformations import to_constant_prices
from ..utils.logging import log_execution_time, log_data_shape
from ..utils.validations import validate_non_empty, check_required_columns
import os
from omegaconf import DictConfig
from pathlib import Path
from hydra.utils import get_original_cwd
import re
import glob
import yaml

def process_gdp_deflator(cfg: DictConfig):
    """Versión corregida con Hydra"""
    # Obtener paths absolutos de forma confiable
    raw_base = Path(cfg.data.raw.base_dir)
    deflator_path = raw_base / cfg.data.raw.gdp_deflator.file
    
    # Validación mejorada
    if not deflator_path.exists():
        available_files = "\n".join([f" - {f}" for f in raw_base.glob("**/*")])
        raise FileNotFoundError(
            f"Archivo de deflactor no encontrado en: {deflator_path}\n"
            f"Archivos disponibles en {raw_base}:\n{available_files}"
        )
    
    df = pd.read_csv(deflator_path)
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    valor_2020 = df[df['observation_date'].dt.year == 2020]['GDPDEF'].iloc[0]
    df['GDPDEF'] = (df['GDPDEF'] / valor_2020) * 100
    
    # Corregido: asegurar que existe el directorio padre
    ensure_dir(deflator_path.parent)
    df.to_csv(deflator_path, index=False)
    return valor_2020, df

@log_execution_time
@log_data_shape
def process_gdp(input_gdp, output_path, cfg):
    """Procesamiento actualizado usando configuración completa"""
    # Permitir tanto path como DataFrame
    if isinstance(input_gdp, str):
        df = pd.read_csv(input_gdp, skiprows=4)
    else:
        df = input_gdp
    
    # Validaciones
    validate_non_empty(df, "PIB")
    check_required_columns(df, ['Country Name', 'Country Code'])
    
    # Filtrar solo Uruguay y convertir a formato largo
    uruguay_df = df[df['Country Code'] == 'URY'].melt(
        id_vars=['Country Name', 'Country Code'],
        var_name='year',
        value_name='gdp'
    )
    
    # Convertir año a numérico y limpiar datos
    uruguay_df['year'] = pd.to_numeric(uruguay_df['year'], errors='coerce')
    uruguay_df = uruguay_df.dropna()
    
    # Ordenar por año y establecer índice
    uruguay_df = uruguay_df.sort_values('year').set_index('year')['gdp']
    
    # Guardar con metadatos
    ensure_dir(os.path.dirname(output_path))
    uruguay_df.to_csv(output_path)
    
    return uruguay_df

def validate_gdp_data(df):
    """Validaciones de calidad de datos"""
    if df.empty:
        raise ValueError("Datos de PIB vacíos")
    
    if 'URY' not in df['Country Code'].values:
        raise ValueError("Datos de Uruguay no encontrados en el dataset")

def save_with_metadata(series, output_path, metadata):
    """Guarda serie con metadatos en CSV"""
    df = series.reset_index()
    df.attrs = metadata
    df.to_csv(output_path, index=False)

def read_gdp_share_file(file_path):
    """Lee un archivo individual de participación en el PIB departamental"""
    print(f"Procesando archivo: {os.path.basename(file_path)}")
    
    # Intentar diferentes codificaciones
    encodings = ['latin1', 'iso-8859-1', 'utf-8']
    
    for encoding in encodings:
        try:
            # Leer el archivo con la codificación actual
            df = pd.read_csv(file_path, sep=';', skiprows=4, encoding=encoding, decimal=',')
            
            # Extraer año del archivo
            with open(file_path, 'r', encoding=encoding) as f:
                header = ''.join([next(f) for _ in range(4)])
                year = int(re.search(r'Año:\s*(\d{4})', header).group(1))
            
            # Limpiar datos
            df = df.rename(columns={df.columns[0]: 'departamento', 'Total': 'participacion'})
            
            # Filtrar solo departamentos (excluir regiones)
            departamentos = [
                'Montevideo', 'Artigas', 'Canelones', 'Cerro Largo', 'Colonia',
                'Durazno', 'Flores', 'Florida', 'Lavalleja', 'Maldonado',
                'Paysandú', 'Río Negro', 'Rivera', 'Rocha', 'Salto',
                'San José', 'Soriano', 'Tacuarembó', 'Treinta y Tres'
            ]
            df = df[df['departamento'].isin(departamentos)]
            
            # Agregar año
            df['año'] = year
            
            print(f"Archivo procesado exitosamente con codificación {encoding}")
            return df[['departamento', 'año', 'participacion']]
            
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error procesando {file_path} con codificación {encoding}: {str(e)}")
            continue
    
    raise ValueError(f"No se pudo leer el archivo {file_path} con ninguna codificación")

def process_gdp_share_raw(input_dir, output_path, years_params):
    """Procesa datos crudos de participación en el PIB departamental"""
    print("\nProcesando datos de participación en PIB departamental...")
    
    # Crear directorio de salida completo (incluyendo subdirectorios)
    output_dir = Path(output_path).parent
    ensure_dir(output_dir) 
    
    # Listar archivos CSV en el directorio
    pattern = os.path.join(input_dir, "Indicador--Participacion*.csv")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos en {pattern}")
    
    print(f"Encontrados {len(files)} archivos para procesar")
    
    # Leer y combinar archivos
    dfs = []
    for file in sorted(files):
        try:
            df = read_gdp_share_file(file)
            if df is not None and not df.empty:
                dfs.append(df)
                print(f"✓ Procesado: {os.path.basename(file)}")
        except Exception as e:
            print(f"✗ Error en {os.path.basename(file)}: {str(e)}")
    
    if not dfs:
        raise ValueError("No se pudo procesar ningún archivo correctamente")
    
    # Combinar todos los años
    df_combined = pd.concat(dfs, ignore_index=True)
    
    # Validar sumas por año
    yearly_sums = df_combined.groupby('año')['participacion'].sum()
    print("\nSuma de participaciones por año:")
    print(yearly_sums)
    
    # Guardar resultados
    ensure_dir(os.path.dirname(output_path))
    df_combined.to_csv(output_path, index=False)
    
    # Crear metadata
    metadata = {
        'dataset': {
            'name': 'Participación departamental en PIB',
            'temporal_coverage': {
                'start': int(df_combined['año'].min()),
                'end': int(df_combined['año'].max()),
                'frequency': 'anual'
            },
            'unidad': 'porcentaje',
            'fuente': 'OPP Uruguay',
            'variables': {
                'departamento': 'Nombre del departamento',
                'año': 'Año de referencia',
                'participacion': 'Participación en el PIB nacional (%)'
            },
            'notas': [
                'Datos consolidados de múltiples archivos anuales',
                'Se excluyeron las agregaciones regionales',
                'Valores expresados en porcentaje del PIB nacional'
            ]
        }
    }
    
    # Guardar metadata
    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    
    return df_combined, metadata 