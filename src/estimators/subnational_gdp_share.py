"""
Estimaciones de participación departamental en PIB
utilizando un modelo de panel con efectos fijos por departamento
y la proporción de población como variable auxiliar,
reinsertando datos reales (2008–2014) antes de la normalización final.
"""
from ..utils.io import ensure_dir, read_file
from ..utils.validations import validate_non_empty, check_required_columns
import pandas as pd
import numpy as np
import statsmodels.api as sm
import os
import yaml

def project_subnational_gdp_share(
    input_path,
    population_path,
    output_path,
    years_params
):
    """
    Proyecta la participación departamental en el PIB combinando:
      - Datos de participación (2008–2014) con pocos años.
      - Datos de población completos (por departamento) para un rango amplio.
    Modelo en panel con efectos fijos por departamento:
       participacion_{d,t} = alpha_d + beta * ratio_{d,t} + error_{d,t}

    ratio_{d,t} = poblacion_{d,t} / poblacion_total_{t}
    alpha_d = intercepto (efecto fijo) de cada depto
    beta = coef. común para ratio
    + Normalización a 100% para cada año.
    + *Reinserción* de los datos reales (2008–2014) antes de normalizar.

    Pasos:
      1) Leer y validar datos de participación (input_path).
      2) Leer y validar datos de población (population_path).
      3) Crear df_ratio = pop_depto / pop_total.
      4) Construir "panel" [depto, año, ratio, participacion] solo en años con datos.
      5) Ajustar OLS: participacion ~ C(departamento) + ratio - 1.
      6) Predecir para todo el rango (start..end) usando df_ratio.
      7) Pivotear => df_final.
      8) *Reinsertar* datos reales en 2008–2014.
      9) Normalizar a 100%.
      10) Guardar CSV, YAML. Devolver df_final, metadata.

    Parámetros
    ----------
    input_path : str
        CSV con [departamento, año, participacion] (ej. 2008–2014).
    population_path : str
        CSV con índice='año', columnas=departamentos, valores=población (1990..2024).
    output_path : str
        Ruta de salida para CSV y metadatos.
    years_params : dict
        {'start': 1990, 'end': 2024}, etc.

    Retorna
    -------
    df_final : pd.DataFrame
        DataFrame con índice=año, columnas=departamentos, valores=participación.
    metadata : dict
        Diccionario con info del proceso.

    Referencias (formato APA 7)
    ---------------------------
    - Wooldridge, J. M. (2019). Introductory Econometrics: A Modern Approach
      (7th ed.). Cengage Learning, p. 470.
    - Baltagi, B. H. (2008). Econometric Analysis of Panel Data (4th ed.).
      John Wiley & Sons, p. 16.
    """

    print("Proyectando participación departamental en PIB con modelo de panel (efectos fijos)...")

    # --------------------------------------------------------------------------
    # 1. Leer y validar datos de participación
    # --------------------------------------------------------------------------
    df_part = read_file(input_path)
    validate_non_empty(df_part, "Participación PIB")
    check_required_columns(df_part, ['departamento', 'año', 'participacion'])
    df_part['año'] = df_part['año'].astype(int)
    df_part.dropna(subset=['departamento', 'año', 'participacion'], inplace=True)
    print(f"Datos de participación cargados y validados desde: {input_path}")

    # --------------------------------------------------------------------------
    # 2. Leer y validar datos de población
    # --------------------------------------------------------------------------
    df_pop = read_file(population_path, index_col='año')
    validate_non_empty(df_pop, "Población")
    df_pop.index = df_pop.index.map(int)
    print(f"Datos de población cargados desde: {population_path}")

    # --------------------------------------------------------------------------
    # 3. Calcular proporción poblacional (ratio)
    # --------------------------------------------------------------------------
    df_pop['total'] = df_pop.sum(axis=1)
    df_ratio = df_pop.drop(columns='total').div(df_pop['total'], axis=0)

    # --------------------------------------------------------------------------
    # 4. Construir el panel
    # --------------------------------------------------------------------------
    panel_data = []
    for i, row in df_part.iterrows():
        depto = row['departamento']
        year = row['año']
        part_val = row['participacion']

        if depto not in df_ratio.columns:
            continue
        if year not in df_ratio.index:
            continue

        ratio_val = df_ratio.loc[year, depto]
        panel_data.append({
            'departamento': depto,
            'año': year,
            'ratio': ratio_val,
            'participacion': part_val
        })

    df_panel = pd.DataFrame(panel_data)
    df_panel.dropna(subset=['ratio','participacion'], inplace=True)
    df_panel.sort_values(by=['departamento','año'], inplace=True)

    if df_panel.empty:
        raise ValueError("No se pudo construir el panel (df_panel vacío).")

    print(f"Panel construido con {df_panel.shape[0]} filas.")

    # --------------------------------------------------------------------------
    # 5. Ajuste OLS con efectos fijos
    # --------------------------------------------------------------------------
    formula = "participacion ~ C(departamento) + ratio - 1"
    model = sm.OLS.from_formula(formula, data=df_panel).fit()
    print("\nResumen del modelo (panel con efectos fijos por dpto + ratio):\n")
    print(model.summary())
    print("\nParámetros estimados:")
    print(model.params)

    # --------------------------------------------------------------------------
    # 6. Proyectar para todo el rango
    # --------------------------------------------------------------------------
    start_year = years_params['start']
    end_year = years_params['end']
    print(f"Proyectando desde {start_year} hasta {end_year}...")

    all_years = range(start_year, end_year + 1)
    projection_list = []
    for depto in df_ratio.columns:
        for year in all_years:
            ratio_val = df_ratio.loc[year, depto] if year in df_ratio.index else np.nan
            projection_list.append({
                'departamento': depto,
                'año': year,
                'ratio': ratio_val
            })

    df_projection = pd.DataFrame(projection_list)
    df_projection['departamento'] = df_projection['departamento'].astype('category')
    df_projection['ratio'] = df_projection['ratio'].interpolate()

    y_hat = model.predict(df_projection)
    y_hat = np.clip(y_hat, 0.1, 70)
    df_projection['participacion'] = y_hat

    # --------------------------------------------------------------------------
    # 7. Pivotear => df_final
    # --------------------------------------------------------------------------
    df_final = df_projection.pivot(index='año', columns='departamento', values='participacion')

    # --------------------------------------------------------------------------
    # 8. Reinsertar valores históricos reales en 2008–2014
    #    (o los que tengas en df_part)
    # --------------------------------------------------------------------------
    for i, row in df_part.iterrows():
        a = row['año']
        d = row['departamento']
        val_real = row['participacion']
        if (a in df_final.index) and (d in df_final.columns):
            df_final.loc[a, d] = val_real

    # --------------------------------------------------------------------------
    # 9. Normalizar a 100%
    # --------------------------------------------------------------------------
    df_final = df_final.div(df_final.sum(axis=1), axis=0) * 100

    # --------------------------------------------------------------------------
    # 10. Guardar resultados (CSV) y metadata
    # --------------------------------------------------------------------------
    ensure_dir(os.path.dirname(output_path))
    df_final.T.to_csv(output_path)
    print(f"\nProyecciones guardadas en: {output_path}")

    metadata = {
        'dataset': {
            'name': 'Proyección de participación (panel FE + reinsertar datos reales)',
            'temporal_coverage': {
                'start': start_year,
                'end': end_year,
                'frequency': 'anual'
            },
            'unidad': 'porcentaje',
            'fuente': 'INE / OPP - Proyección propia',
            'methodology': {
                'type': 'Panel data model (Fixed Effects by department)',
                'formula': 'participacion ~ C(departamento) + ratio - 1',
                'normalization': 'la suma de departamentos es 100% por año',
                'ratio': 'poblacion_depto / poblacion_total por año',
                'reinsert_real_data': True
            },
            'notas': [
                'Datos reales 2008–2014 se reinsertan antes de normalizar.',
                'Pocos años para participación => R² alto y extrapolación incierta.',
                'Cada departamento tiene un intercepto, y ratio con pendiente común.'
            ]
        }
    }

    metadata_path = os.path.join(os.path.dirname(output_path), 'metadata.yaml')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, allow_unicode=True, sort_keys=False)
    print(f"Metadata guardada en: {metadata_path}")

    return df_final, metadata

