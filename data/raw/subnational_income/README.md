# Ingresos Municipales por Departamento - Uruguay

## Fuente Original
- **Proveedor**: Observatorio Territorio Uruguay (OPP)
- **Cobertura temporal**: 1989-2023
- **Método de Obtención**: Descarga manual desde [portal OPP](https://otu.opp.gub.uy)
- **Última Actualización**: 2023-12-31

## Estructura del Dataset
- **Formato**: Excel (.xlsx)
- **Columnas Principales**:
  - Clasificación administrativa (ORIGEN, NATURALEZA, RUBRO, SUBRUBRO)
  - Montos en pesos constantes 2020 (ESTIMADO.PRESUPUESTADO, RECAUDADO)
  - Identificación geográfica (COD.DEPARTAMENTO, DEPARTAMENTO)

## Variables Clave
- **Cobertura Geográfica**:
  - 19 departamentos (excepto Montevideo 1989-2006)
  - Códigos INE oficiales
- **Métodos Estadísticos**:
  - Deflactación con IPC base 2020
  - Clasificación presupuestal homologada

## Procesamiento Requerido
1. **Limpieza inicial**:
   - Convertir "No Aplica" a valores nulos
   - Normalizar nombres de departamentos según shapefile oficial
   - Unificar formato decimal (coma → punto)

2. **Imputación de datos faltantes**:
   - Estimación valores Montevideo 1989-2006
   - Completar celdas vacías con promedio departamental/anual

3. **Integración con otras series**:
   - Cruce con datos poblacionales (per cápita)
   - Comparación con gastos municipales
   - Análisis de presión tributaria

