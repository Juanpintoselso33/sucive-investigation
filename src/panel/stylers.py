"""
Funciones de estilizado para visualización de paneles de datos
"""
from typing import List, Dict, Optional
import pandas as pd

def style_panel(
    df: pd.DataFrame,
    numeric_cols: List[str],
    index_cols: Optional[List[str]] = None,
    format_dict: Optional[Dict[str, str]] = None,
    highlight_cols: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Aplica estilos al panel para mejor visualización.
    
    Args:
        df: Panel de datos
        numeric_cols: Columnas numéricas a formatear
        index_cols: Columnas a usar como índice
        format_dict: Diccionario de formatos por columna
        highlight_cols: Columnas a resaltar con colores
    """
    # Configuración por defecto
    default_formats = {
        'recaudacion': '{:,.0f}',
        'pib': '{:,.0f}',
        'poblacion': '{:,.0f}',
        'participacion': '{:.2f}%'
    }
    
    # Combinar con formatos personalizados
    if format_dict:
        default_formats.update(format_dict)
    
    # Crear copia y establecer índice si especificado
    styled_df = df.copy()
    if index_cols:
        styled_df = styled_df.set_index(index_cols)
    
    # Aplicar estilos
    return (styled_df.style
        # Formato numérico
        .format({col: fmt for col, fmt in default_formats.items() 
                if col in styled_df.columns})
        # Resaltado condicional
        .background_gradient(
            subset=highlight_cols.keys() if highlight_cols else None,
            cmap='YlOrRd'
        )
        # Estilos generales
        .set_properties(**{
            'text-align': 'right',
            'font-family': 'Roboto, sans-serif',
            'white-space': 'nowrap',
            'vertical-align': 'middle'
        })
        .set_table_styles([
            # Estilo general de la tabla
            {'selector': 'table', 'props': [
                ('margin', '0 auto'),
                ('border-collapse', 'collapse'),
                ('width', '100%'),
                ('max-width', '1000px'),
                ('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
            ]},
            # Estilo de encabezados
            {'selector': 'thead', 'props': [
                ('background-color', '#f8f9fa'),
                ('border-bottom', '2px solid #dee2e6')
            ]},
            {'selector': 'th', 'props': [
                ('color', '#495057'),
                ('font-weight', '600'),
                ('text-align', 'center'),
                ('padding', '12px 15px'),
                ('font-size', '0.95em'),
                ('letter-spacing', '0.5px'),
                ('text-transform', 'uppercase'),
                ('vertical-align', 'middle'),
                ('border-bottom', '2px solid #dee2e6')
            ]},
            # Estilo de celdas
            {'selector': 'td', 'props': [
                ('padding', '10px 15px'),
                ('vertical-align', 'middle'),
                ('border-bottom', '1px solid #e9ecef'),
                ('color', '#212529'),
                ('font-size', '0.9em')
            ]},
            # Estilo hover en filas
            {'selector': 'tbody tr:hover', 'props': [
                ('background-color', '#f8f9fa')
            ]},
            # Estilo para filas alternas
            {'selector': 'tbody tr:nth-child(odd)', 'props': [
                ('background-color', '#ffffff')
            ]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [
                ('background-color', '#f9fafb')
            ]}
        ])
    )