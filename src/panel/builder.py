from typing import List, Dict, Optional, Union, Any
import pandas as pd
from .transformers import to_long_format
from .validators import validate_panel_totals
from .stylers import style_panel

class PanelBuilder:
    """Constructor flexible de panel de datos."""
    
    def __init__(self):
        self.panel = None
        self.transformations = {}
        
    def add_variable(
        self,
        data: pd.DataFrame,
        variable_name: str,
        transformation_config: Dict[str, Any]
    ) -> 'PanelBuilder':
        """
        Agrega una variable al panel con configuración flexible.
        
        Args:
            data: DataFrame fuente
            variable_name: Nombre de la variable en el panel final
            transformation_config: Configuración de la transformación
                {
                    'id_vars': str,
                    'var_name': str,
                    'value_name': str,
                    'rename_cols': Dict[str, str],
                    'merge_cols': List[str],
                    'merge_how': str
                }
        """
        # Obtener la función de transformación apropiada
        transform_func = transformation_config['transform_func']
        
        # Aplicar la transformación específica
        df_long = transform_func(data, transformation_config)
        
        # Si es el primer DataFrame, inicializar el panel
        if self.panel is None:
            self.panel = df_long
            return self
            
        # Asegurar que las columnas de merge tengan el mismo tipo
        merge_cols = transformation_config['merge_cols']
        for col in merge_cols:
            # Convertir a int64 si la columna es 'año'
            if col == 'año':
                df_long[col] = df_long[col].astype('int64')
                self.panel[col] = self.panel[col].astype('int64')
            # Para otras columnas, convertir a object
            else:
                df_long[col] = df_long[col].astype('object')
                self.panel[col] = self.panel[col].astype('object')
        
        # Merge con panel existente
        self.panel = self.panel.merge(
            df_long,
            on=['año', 'departamento'],
            how='left',
            validate='1:1'
        )
        
        return self
    
    def sort(self, columns: List[str]) -> 'PanelBuilder':
        """Ordena el panel por columnas especificadas."""
        if self.panel is not None:
            self.panel = self.panel.sort_values(columns)
        return self
    
    def validate(
        self,
        group_col: str,
        sum_cols: List[str]
    ) -> pd.DataFrame:
        """Valida totales por grupo."""
        return validate_panel_totals(
            df=self.panel,
            group_col=group_col,
            sum_cols=sum_cols
        )
    
    def build(self) -> pd.DataFrame:
        """Construye el panel final."""
        if self.panel is None:
            raise ValueError("No se han agregado datos al panel")
        return self.panel.copy()

    def display(
        self,
        numeric_cols: Optional[List[str]] = None,
        index_cols: Optional[List[str]] = None,
        format_dict: Optional[Dict[str, str]] = None,
        highlight_cols: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Muestra el panel con estilos aplicados.
        
        Args:
            numeric_cols: Columnas numéricas a formatear
            index_cols: Columnas a usar como índice
            format_dict: Diccionario de formatos por columna
            highlight_cols: Columnas a resaltar con colores
        """
        if self.panel is None:
            raise ValueError("No hay panel para mostrar")
        
        if numeric_cols is None:
            numeric_cols = self.panel.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        return style_panel(
            df=self.panel,
            numeric_cols=numeric_cols,
            index_cols=index_cols,
            format_dict=format_dict,
            highlight_cols=highlight_cols
        )