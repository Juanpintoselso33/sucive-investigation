from typing import Dict, Any
import pandas as pd
import unicodedata

def normalize_text(text: str) -> str:
    """Normaliza el texto eliminando tildes y convirtiendo a minúsculas"""
    normalized = unicodedata.normalize('NFKD', str(text))
    normalized = u"".join([c for c in normalized if not unicodedata.combining(c)])
    return normalized.lower()

def transform_tax_data(data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Transforma datos de recaudación"""
    df = data.copy()
    
    # Convertir a formato largo
    df_long = pd.melt(
        df,
        id_vars='DEPARTAMENTO',
        var_name='año',
        value_name='recaudacion'
    )
    
    # Renombrar y convertir tipos
    df_long['departamento'] = df_long['DEPARTAMENTO'].str.strip().apply(normalize_text)
    df_long['año'] = pd.to_numeric(df_long['año'])
    df_long = df_long.drop('DEPARTAMENTO', axis=1)
    
    return df_long

def transform_gdp_data(data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Transforma datos de PIB"""
    df = data.copy()
    
    # Convertir años a columnas y departamentos a filas
    df_long = df.melt(
        id_vars='Unnamed: 0',
        var_name='departamento',
        value_name='pib'
    )
    
    # Renombrar y convertir tipos
    df_long = df_long.rename(columns={'Unnamed: 0': 'año'})
    df_long['año'] = pd.to_numeric(df_long['año'])
    df_long['departamento'] = df_long['departamento'].str.strip().apply(normalize_text)
    
    return df_long

def transform_pop_data(data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Transforma datos de población"""
    df = data.copy()
    
    # Ya tiene el año como columna, solo necesitamos convertir a formato largo
    df_long = df.melt(
        id_vars='año',
        var_name='departamento',
        value_name='poblacion'
    )
    
    # Convertir tipos y normalizar departamentos
    df_long['año'] = pd.to_numeric(df_long['año'])
    df_long['departamento'] = df_long['departamento'].str.strip().apply(normalize_text)
    
    return df_long