"""
Validaciones para paneles de datos
"""
import pandas as pd
from typing import List

def validate_panel_totals(
    df: pd.DataFrame,
    group_col: str,
    sum_cols: List[str]
) -> pd.DataFrame:
    """
    Valida que los totales por grupo sean consistentes.
    
    Args:
        df: Panel de datos
        group_col: Columna de agrupación (ej: 'año')
        sum_cols: Columnas a sumar y validar
    """
    # Calcular totales por grupo
    totals = df.groupby(group_col)[sum_cols].sum()
    
    # Calcular porcentajes del total
    for col in sum_cols:
        totals[f'{col}_pct'] = (df.groupby(group_col)[col].sum() / 
                               df[col].sum() * 100).round(2)
    
    return totals