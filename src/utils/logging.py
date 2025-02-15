import time
import pandas as pd
from functools import wraps

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"▶ Iniciando {func.__name__}...")
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"✓ {func.__name__} completado en {duration:.2f}s")
        return result
    return wrapper

def log_data_shape(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, pd.DataFrame):
            print(f"📊 Dimensiones de datos: {result.shape[0]} filas x {result.shape[1]} columnas")
        elif isinstance(result, pd.Series):
            print(f"📊 Longitud de la serie: {len(result)} elementos")
        return result
    return wrapper 