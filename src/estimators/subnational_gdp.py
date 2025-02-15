"""
Estimación del PIB departamental usando participación proyectada
y PIB nacional histórico/proyectado
"""
from ..utils.io import ensure_dir, read_file
from ..utils.validations import validate_non_empty
import pandas as pd
import os
import yaml

def estimate_subnational_gdp(
    gdp_share_path,
    national_gdp_path,
    output_path,
    years_params
):
    """
    Calcula el PIB departamental combinando:
    - Participación departamental proyectada (%)
    - PIB nacional histórico/proyectado (USD constantes)
    
    PIB_depto = (Participación_depto/100) * PIB_nacional
    """
    print("\nEstimando PIB departamental...")
    
    # 1. Cargar y validar datos
    df_share = read_file(gdp_share_path)
    df_gdp = read_file(national_gdp_path, index_col='year')
    
    validate_non_empty(df_share, "Participación PIB")
    validate_non_empty(df_gdp, "PIB nacional")
    
    # Reestructurar df_share
    df_share = df_share.set_index('departamento').T
    df_share.index = pd.to_numeric(df_share.index)
    
    # 2. Alinear años
    common_years = df_share.index.intersection(df_gdp.index)
    
    if len(common_years) == 0:
        raise ValueError("No hay años en común entre los datasets")
    
    df_share = df_share.loc[common_years]
    df_gdp = df_gdp.loc[common_years]
    
    # 3. Calcular PIB departamental
    df_final = df_share.multiply(df_gdp['gdp'], axis=0) / 100
    
    # 4. Validar resultados
    validation = pd.DataFrame({
        'sum_departamentos': df_final.sum(axis=1),
        'pib_nacional': df_gdp['gdp']
    })
    print("\nValidación de totales:")
    print(validation)
    
    # 5. Guardar resultados
    ensure_dir(os.path.dirname(output_path))
    df_final.to_csv(output_path)
    print(f"\nResultados guardados en: {output_path}")
    
    # 6. Crear metadata
    start_year = int(common_years.min())
    end_year = int(common_years.max())
    
    metadata = {
        'dataset': {
            'name': 'PIB departamental estimado',
            'temporal_coverage': {
                'start': start_year,
                'end': end_year,
                'frequency': 'anual'
            },
            'unidad': 'USD constantes 2020',
            'fuente': 'Estimación propia basada en:',
            'fuentes_base': [
                'PIB nacional (Banco Mundial)',
                'Participación departamental (OPP + proyección)'
            ],
            'metodologia': {
                'descripcion': 'Distribución del PIB nacional según participación',
                'formula': 'PIB_depto = (Participación_depto/100) * PIB_nacional'
            },
            'notas': [
                'Valores en dólares constantes de 2020',
                'Basado en participación departamental proyectada',
                'Suma departamental puede diferir levemente del total nacional'
            ]
        }
    }
    
    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    print(f"Metadata guardada en: {metadata_path}")
    
    return df_final, metadata