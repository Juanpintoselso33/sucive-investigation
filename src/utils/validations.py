import pandas as pd

def check_required_columns(df: pd.DataFrame, required_columns: list):
    """Valida que existan las columnas requeridas"""
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes: {missing}")

def validate_non_empty(df: pd.DataFrame, context: str = ""):
    """Valida que el DataFrame no esté vacío"""
    if df.empty:
        raise ValueError(f"Datos vacíos en contexto: {context}")
    
def validate_year_range(years: dict):
    """Valida rango temporal coherente"""
    if years['start'] > years['end']:
        raise ValueError("Año de inicio mayor que año final") 