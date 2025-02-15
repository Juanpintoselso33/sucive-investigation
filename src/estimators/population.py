"""
Estimaciones y proyecciones poblacionales
"""
from ..utils.io import ensure_dir, read_file
from ..utils.validations import validate_non_empty, check_required_columns
import pandas as pd
import os
import yaml

def project_population(input_path, output_path, years_params):
    """Proyecta población departamental"""
    print("Proyectando población departamental...")
    
    # Cargar y validar datos
    df = read_file(input_path)
    validate_non_empty(df, "Población")
    check_required_columns(df, ['Departamento', '1996', '2011', '2023'])
    
    # Obtener años de proyección
    años_completos = range(years_params['start'], years_params['end'] + 1)
    
    # Proyectar población
    df_proyectado = pd.DataFrame()
    
    for depto in df['Departamento'].unique():
        depto_df = df[df['Departamento'] == depto].copy()
        
        # Crear serie temporal completa
        anual_df = pd.DataFrame({'año': años_completos})
        
        # Mapear datos censales conocidos
        censos = {
            1996: int(depto_df['1996'].values[0]),
            2011: int(depto_df['2011'].values[0]),
            2023: int(depto_df['2023'].values[0])
        }
        
        # Interpolación lineal entre censos
        anual_df['poblacion'] = anual_df['año'].apply(lambda x: censos.get(x, None))
        anual_df['poblacion'] = anual_df['poblacion'].interpolate(method='linear')
        
        # Extrapolación usando tasas de crecimiento
        tasa_pre = float(depto_df['Tasa 1996-2011'].values[0])
        tasa_post = float(depto_df['Tasa 2011-2023'].values[0])
        
        # Proyección pre-1996
        mask_pre = anual_df['año'] < 1996
        anual_df.loc[mask_pre, 'poblacion'] = censos[1996] * (1 + tasa_pre) ** (anual_df.loc[mask_pre, 'año'] - 1996)
        
        # Proyección post-2023
        mask_post = anual_df['año'] > 2023
        anual_df.loc[mask_post, 'poblacion'] = censos[2023] * (1 + tasa_post) ** (anual_df.loc[mask_post, 'año'] - 2023)
        
        # Convertir todas las poblaciones a enteros después de todas las proyecciones
        anual_df['poblacion'] = anual_df['poblacion'].round().astype(int)
        
        anual_df['departamento'] = depto
        df_proyectado = pd.concat([df_proyectado, anual_df])
    
    # Pivotar para formato final
    df_final = df_proyectado.pivot(
        index='año',
        columns='departamento',
        values='poblacion'
    )
    
    # Crear metadata
    metadata = {
        'dataset': {
            'name': 'Población departamental proyectada',
            'temporal_coverage': {
                'start': years_params['start'],
                'end': years_params['end'],
                'frequency': 'anual'
            },
            'unidad': 'habitantes',
            'fuente': 'INE Uruguay - Proyección propia',
            'variables': {
                'año': 'Año de referencia',
                'departamento': 'Nombre del departamento',
                'poblacion': 'Población estimada'
            },
            'notas': [
                'Interpolación lineal entre censos 1996-2011-2023',
                'Extrapolación exponencial para años fuera del rango censal',
                'Tasas de crecimiento departamentales aplicadas',
                f'Año base para proyecciones anteriores: 1996',
                f'Año base para proyecciones posteriores: 2023'
            ]
        }
    }
    
    # Guardar resultados
    ensure_dir(os.path.dirname(output_path))
    df_final.to_csv(output_path)
    
    # Guardar metadata
    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    
    return df_final, metadata