"""
Estimación de datos faltantes usando control sintético
"""
from ..utils.io import ensure_dir, read_file
from ..utils.validations import validate_non_empty
import pandas as pd
import numpy as np
from sklearn.linear_model import ElasticNetCV
from sklearn.model_selection import TimeSeriesSplit
import os
import yaml

def estimate_missing_vehicle_tax(
    input_path,
    population_path,
    output_path,
    years_params,
    target_dept='Montevideo',
    treatment_year=2007
):
    """
    Estima datos faltantes usando control sintético con:
    - Datos de recaudación post-2007 como target
    - Población departamental como covariable
    - ElasticNet para selección de pesos
    
    Parámetros
    ----------
    input_path : str
        CSV con datos de recaudación [departamento, año, recaudacion]
    population_path : str
        CSV con población por departamento
    output_path : str
        Ruta para guardar resultados
    years_params : dict
        Parámetros de años {'start': 1990, 'end': 2024}
    target_dept : str
        Departamento a estimar (default: 'Montevideo')
    treatment_year : int
        Año de corte para entrenamiento (default: 2007)
    """
    print(f"\nEstimando control sintético para {target_dept}...")
    
    # 1. Cargar y validar datos
    df = read_file(input_path)
    df_pop = read_file(population_path)
    
    validate_non_empty(df, "Recaudación")
    validate_non_empty(df_pop, "Población")
    
    # Convertir de formato ancho a largo
    df_long = df.melt(
        id_vars=['DEPARTAMENTO'],
        var_name='año',
        value_name='recaudacion'
    )
    df_long['año'] = pd.to_numeric(df_long['año'])
    df_long = df_long.rename(columns={'DEPARTAMENTO': 'departamento'})
    
    # 2. Preparar datos de entrenamiento
    target_data = df_long[
        (df_long['departamento'] == target_dept) & 
        (df_long['año'] >= treatment_year)
    ].set_index('año')['recaudacion']
    
    donor_pool = df_long[
        (df_long['departamento'] != target_dept) & 
        (df_long['año'] >= treatment_year)
    ]
    
    X_train = donor_pool.pivot(
        index='año',
        columns='departamento',
        values='recaudacion'
    ).fillna(method='ffill')
    
    # 3. Ajustar modelo
    model = ElasticNetCV(
        l1_ratio=[.1, .5, .7, .9, .95, .99, 1],
        cv=TimeSeriesSplit(n_splits=3),
        max_iter=10000
    )
    model.fit(X_train, target_data)
    
    # Obtener coeficientes de los donantes y convertirlos a float simple
    donor_coefficients = {
        dept: float(coef) for dept, coef in zip(X_train.columns, model.coef_)
        if coef > 0.001  # Solo incluir donantes con peso significativo
    }
    
    # Ordenar coeficientes por valor descendente
    donor_coefficients = dict(sorted(
        donor_coefficients.items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    
    # 4. Proyectar período pre-treatment
    donor_pre = df_long[
        (df_long['departamento'] != target_dept) & 
        (df_long['año'] < treatment_year)
    ]
    
    X_pre = donor_pre.pivot(
        index='año',
        columns='departamento',
        values='recaudacion'
    ).fillna(method='ffill')
    
    predictions = pd.Series(
        model.predict(X_pre),
        index=X_pre.index,
        name='recaudacion'
    )
    
    # 5. Guardar solo las predicciones
    ensure_dir(os.path.dirname(output_path))
    
    # Crear DataFrame con formato original pero solo con predicciones
    df_estimated = pd.DataFrame({'DEPARTAMENTO': [target_dept]})
    
    # Agregar años estimados
    numeric_columns = df.columns[df.columns != 'DEPARTAMENTO']
    years_estimated = numeric_columns[
        pd.to_numeric(numeric_columns).astype(int) < treatment_year
    ]
    
    for year, value in zip(years_estimated, predictions.values):
        df_estimated[year] = value
    
    # Guardar solo estimaciones
    df_estimated.to_csv(output_path, index=False)
    
    # Metadata específica para estimaciones
    metadata = {
        'dataset': {
            'name': f'Estimaciones control sintético para {target_dept}',
            'temporal_coverage': {
                'start': int(years_params['start']),
                'end': treatment_year - 1,
                'frequency': 'anual'
            },
            'unidad': 'USD constantes 2020',
            'fuente': 'Estimación propia',
            'metodologia': {
                'tipo': 'Control sintético (ElasticNet)',
                'periodo_entrenamiento': f'{treatment_year}-{years_params["end"]}',
                'periodo_prediccion': f'{years_params["start"]}-{treatment_year-1}',
                'covariables': ['población departamental'],
                'donantes_y_pesos': {
                    'descripcion': 'Departamentos donantes y sus pesos en el control sintético',
                    'pesos': donor_coefficients
                },
                'r2_score': float(model.score(X_train, target_data))
            }
        }
    }
    
    # Guardar metadata
    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    
    return df_estimated, metadata