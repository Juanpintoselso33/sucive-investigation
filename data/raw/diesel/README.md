# Ventas de Diesel por Departamento - Uruguay

## Fuente Original
- **Proveedor**: [Econuy](https://github.com/rxavier/econuy)
- **Serie**: `diesel` (Datos mensuales 2004-2024)
- **Método de Obtención**: Descarga directa vía API econuy
- **Última Actualización**: 2024-03-31

## Estructura del Archivo
- **Primeras 10 filas**: Metadatos técnicos (no modificar)
- **Datos reales**: Desde fila 11 en adelante
- **Columnas**:
  - `Name`: Fecha en formato YYYY-MM-DD (fin de mes)
  - 20 columnas departamentales
  - `Total`: Suma nacional consolidada

## Variables Clave
- **Unidad**: Metros cúbicos (consistentes en todas las columnas)
- **Frecuencia**: Mensual
- **Periodo Cubierto**: 2004-01-31 a 2024-07-31
- **Cobertura Geográfica**:
  - 19 departamentos + Montevideo
  - División especial de Canelones (balneario/resto)

## Notas de Procesamiento
1. **Transformaciones requeridas**:
   - Eliminar filas de metadatos (primeras 10)
   - Convertir fechas a formato estándar
   - Normalizar nombres de departamentos según shapefile oficial
2. **Integración con otras series**:
   - Deflactar usando IPC base 2020
   - Cruce con datos de patentes vehiculares
   - Correlación con indicadores económicos departamentales

## Relación con Pipeline
- **Script de procesamiento**: `1_Procesamiento_Datos.ipynb` (celdas 45-58)
- **Dependencias**:
  ```yaml
  PATHS:
    RAW:
      nafta: datos/raw/nafta/diesel_sales.csv
    PROCESADOS:
      nafta: datos/processed/nafta/diesel_anual.csv
  ```
- **Salida final**: Serie anual normalizada 2004-2023 para análisis panel