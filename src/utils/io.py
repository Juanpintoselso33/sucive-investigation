"""
Funciones de entrada/salida
"""
import os
import pandas as pd
from pathlib import Path

def ensure_dir(path):
    """
    Asegura que el directorio padre del path existe, creándolo si es necesario.
    
    Args:
        path: Path al archivo o directorio (str o Path)
    """
    if path:
        path = Path(str(path))
        # Si el path termina en una extensión, asumimos que es un archivo
        # y creamos su directorio padre
        if path.suffix:
            os.makedirs(str(path.parent), exist_ok=True)
        # Si no tiene extensión, asumimos que es un directorio
        else:
            os.makedirs(str(path), exist_ok=True)

def read_file(file_path, **kwargs):
    """Lee un archivo según su extensión"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path, **kwargs)
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(file_path, **kwargs)
    else:
        raise ValueError(f"Formato de archivo no soportado: {ext}")

def save_with_metadata(df: pd.DataFrame, output_path: str, metadata: dict = None):
    """Guarda DataFrame con metadatos en CSV"""
    ensure_dir(output_path)
    if metadata:
        df = add_metadata(df, metadata)
    df.to_csv(output_path, index=False)

def load_data_with_metadata(input_path: str) -> pd.DataFrame:
    """Carga DataFrame preservando metadatos"""
    df = read_file(input_path)
    df.attrs = get_csv_metadata(input_path)
    return df

def get_csv_metadata(file_path: str) -> dict:
    """Obtiene metadatos de archivos CSV (si existen)"""
    # Implementación para leer metadatos de comentarios en CSV
    metadata = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                key, value = line[1:].strip().split(':', 1)
                metadata[key.strip()] = value.strip()
            else:
                break
    return metadata 