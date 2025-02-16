"""
Transformaciones para construcción de paneles de datos
"""
from typing import Dict, List, Optional, Union, Callable
import pandas as pd
import numpy as np
import unicodedata

def normalize_text(text):
    """
    Normaliza el texto eliminando tildes y convirtiendo a minúsculas
    """
    # Normalizar Unicode y eliminar diacríticos
    normalized = unicodedata.normalize('NFKD', text)
    normalized = u"".join([c for c in normalized if not unicodedata.combining(c)])
    # Convertir a minúsculas
    return normalized.lower()

def to_long_format(
    df: pd.DataFrame,
    id_vars: Union[str, List[str]],
    var_name: str,
    value_name: str,
    rename_cols: Optional[Dict[str, str]] = None,
    date_cols: Optional[List[str]] = None,
    numeric_cols: Optional[List[str]] = None,
    drop_na: bool = True
) -> pd.DataFrame:
    """
    Convierte datos de formato ancho a largo con opciones de transformación.
    
    Args:
        df: DataFrame en formato ancho
        id_vars: Columna(s) identificadora(s)
        var_name: Nombre para la columna de variables
        value_name: Nombre para la columna de valores
        rename_cols: Diccionario para renombrar columnas
        date_cols: Columnas a convertir a datetime
        numeric_cols: Columnas a convertir a numeric
        drop_na: Si eliminar filas con NA
    """
    # Copia para no modificar original
    df = df.copy()
    
    # Convertir fechas si especificado
    if date_cols:
        for col in date_cols:
            df[col] = pd.to_datetime(df[col])
            
    # Convertir numéricos si especificado
    if numeric_cols:
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Transformar a formato largo
    df_long = df.melt(
        id_vars=id_vars,
        var_name=var_name,
        value_name=value_name
    )
    
    # Renombrar columnas si especificado
    if rename_cols:
        df_long = df_long.rename(columns=rename_cols)
    
    # Eliminar NA si especificado
    if drop_na:
        df_long = df_long.dropna()
        
    return df_long

def apply_transformations(
    df: pd.DataFrame,
    transformations: Dict[str, Union[str, Callable]]
) -> pd.DataFrame:
    """
    Aplica transformaciones específicas a columnas.
    
    Args:
        df: DataFrame a transformar
        transformations: Diccionario de transformaciones
            {'column_name': 'int'|'float'|'datetime'|callable}
    """
    df = df.copy()
    
    for col, transform in transformations.items():
        if col not in df.columns:
            continue
            
        if transform == 'int':
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        elif transform == 'float':
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif transform == 'datetime':
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif callable(transform):
            df[col] = df[col].map(transform)
            
    return df

def normalize_values(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    method: str = 'sum'
) -> pd.DataFrame:
    """
    Normaliza valores por grupo (ej. porcentajes que sumen 100).
    
    Args:
        df: DataFrame a normalizar
        group_col: Columna de agrupación
        value_col: Columna a normalizar
        method: 'sum' o 'max' para normalización
    """
    df = df.copy()
    
    if method == 'sum':
        totals = df.groupby(group_col)[value_col].transform('sum')
        df[value_col] = (df[value_col] / totals * 100).round(2)
    elif method == 'max':
        maxs = df.groupby(group_col)[value_col].transform('max')
        df[value_col] = (df[value_col] / maxs * 100).round(2)
        
    return df

def transform_tax_data(df):
    # Copiar el DataFrame original
    df = df.copy()
    
    # Normalizar nombres de departamentos
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].apply(normalize_text)
    
    # Resto de la transformación...
    df = df.melt(id_vars=['DEPARTAMENTO'], 
                 var_name='año', 
                 value_name='recaudacion')
    df = df.rename(columns={'DEPARTAMENTO': 'departamento'})
    df['año'] = df['año'].astype(int)
    return df

def transform_gdp_data(df):
    df = df.copy()
    
    # Renombrar la columna de año
    df = df.rename(columns={'Unnamed: 0': 'año'})
    
    # Convertir a formato largo
    df = df.melt(id_vars=['año'], var_name='departamento', value_name='pib')
    
    # Normalizar nombres de departamentos
    df['departamento'] = df['departamento'].apply(normalize_text)
    
    return df

def transform_pop_data(df):
    df = df.copy()
    
    # Convertir a formato largo
    df = df.melt(id_vars=['año'], var_name='departamento', value_name='poblacion')
    
    # Normalizar nombres de departamentos
    df['departamento'] = df['departamento'].apply(normalize_text)
    
    return df