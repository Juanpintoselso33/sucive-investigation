# Producto Interno Bruto Mundial - Datos del Banco Mundial (1960-2023)

## Fuente de Datos
- **Proveedor**: Banco Mundial
- **Base de Datos**: Indicadores del Desarrollo Mundial
- **Indicador**: PIB (US$ a precios actuales)
- **Última Actualización**: 16 de diciembre de 2024

## Estructura del Dataset
- **Formato**: Archivo CSV
- **Cobertura Temporal**: 1960-2023 (anual)
- **Cobertura Geográfica**: Mundial (todos los países + agregados regionales)
- **Columnas Principales**:
  - Nombre del País
  - Código del País (ISO 3 letras)
  - Nombre del Indicador
  - Código del Indicador
  - Años (1960-2023)

## Descripción de Variables
- **Valores del PIB**: Medidos en dólares estadounidenses corrientes
- **Definición**: Suma del valor agregado bruto de todos los productores residentes más impuestos a los productos menos subsidios
- **Metodología**: Datos de cuentas nacionales del Banco Mundial y archivos de datos de Cuentas Nacionales de la OCDE

## Características de los Datos
1. **Valores Faltantes**:
   - No todos los países tienen datos para todos los años
   - Los años más antiguos (1960s-1970s) tienen más valores faltantes
   - Algunos países solo tienen datos recientes

2. **Casos Especiales**:
   - Incluye agregados regionales (ej: "Mundo", "Mundo Árabe")
   - Contiene agregados por grupos de ingresos (ej: "Ingreso medio alto")
   - Incluye algunos territorios y entidades no soberanas

## Notas de Uso
- Los valores están en términos nominales (no ajustados por inflación)
- Para análisis de series temporales, considerar la conversión a precios constantes
- Los agregados regionales pueden filtrarse si solo se necesita análisis a nivel país
- Algunos nombres y códigos de países pueden haber cambiado con el tiempo

## Licencia
Este conjunto de datos se distribuye bajo licencia CC-BY-4.0, siguiendo los términos de uso de datos del Banco Mundial.