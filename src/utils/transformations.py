"""
Transformaciones comunes de datos (completado)
"""
import pandas as pd

def to_constant_prices(df, deflator_df, years_params, value_col='pib'):
    """Convierte valores a precios constantes (vectorizado)"""
    df = df.melt(
        id_vars=['Country Name', 'Country Code'],
        value_vars=[str(y) for y in range(years_params['start'], years_params['end']+1)],
        var_name='year',           # Corregido: var_names -> var_name
        value_name=value_col       # Corregido: value_names -> value_name
    )
    
    df = df.merge(
        deflator_df[['year', 'GDPDEF']],
        on='year',
        how='left'
    )
    
    df[value_col] = (df[value_col] * 100 / df['GDPDEF']).round(2)
    return df[['year', value_col]].set_index('year').squeeze()

def normalize_to_base_year(series, base_year=2020):
    """Normaliza una serie temporal a un año base"""
    base_value = series[series.index.year == base_year].iloc[0]
    return (series / base_value) * 100

def vectorized_conversion(values, factors):
    """Conversión vectorizada usando operaciones de pandas"""
    return values * (100 / factors)

def resample_annual(series):
    """Convierte series temporales a frecuencia anual"""
    return series.resample('YE').mean()

def filter_by_years(df, years_params):
    """Filtra DataFrame por años"""
    return df[
        (df['year'] >= years_params['start']) & 
        (df['year'] <= years_params['end'])
    ] 

def add_metadata(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """Agrega metadatos como atributos del DataFrame"""
    df.attrs.update(metadata)
    return df

def convert_to_usd(values: pd.Series, exchange_rate: float) -> pd.Series:
    """Conversión vectorizada a USD usando tipo de cambio"""
    return values / exchange_rate

def calculate_real_values(nominal_values: pd.Series, deflator: pd.Series) -> pd.Series:
    """Calcula valores reales usando serie de deflactor"""
    return (nominal_values * deflator.iloc[-1]) / deflator 

def safe_convert_to_numeric(series: pd.Series) -> pd.Series:
    """Conversión segura a numérico con manejo de errores"""
    return pd.to_numeric(series, errors='coerce')

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza nombres de columnas"""
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
    )
    return df 