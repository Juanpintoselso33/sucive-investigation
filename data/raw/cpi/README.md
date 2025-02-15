# Índice de Precios al Consumidor (IPC) - Uruguay

## Fuente Original
- **Proveedor**: [Econuy](https://github.com/rxavier/econuy)
- **Serie**: `cpi` (Datos mensuales 1937-2024)
- **Método de Obtención**: Descarga directa vía econuy
- **Última Actualización**: 2024-03-31

## Estructura del Archivo
- **Formato**: CSV
- **Encoding**: UTF-8
- **Columnas**:
  - `fecha`: Fecha en formato YYYY-MM-DD (fin de mes)
  - `cpi`: Índice de Precios al Consumidor base 2020=100

## Variables Clave
- **Unidad**: Índice (2020=100)
- **Frecuencia**: Mensual
- **Periodo Cubierto**: 1937-07-31 a 2024-12-31
- **Ajustes metodológicos**:
  - Revisión 2016 (Nueva canasta)
  - Revisión 2020 (Actualización ponderaciones)

## Notas de Uso
1. **Serie histórica reconstruida**: Combina múltiples bases metodológicas
2. **Procesamiento requerido**:
   - Convertir a frecuencia anual (promedio anual)
   - Normalizar según parámetros del proyecto (ver `1_Procesamiento_Datos.ipynb`)
3. **Integración con otros datasets**:
   - Usar para deflactar series nominales
   - Cruce con datos de patentes y PIB departamental

