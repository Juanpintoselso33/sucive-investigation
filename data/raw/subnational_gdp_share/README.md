# Participación Departamental en el PIB Nacional - Uruguay

## Fuente Original
- **Proveedor**: Observatorio Territorio Uruguay (OPP)
- **Cobertura temporal**: 2008-2014
- **Método de Obtención**: Descarga manual desde portal OPP
- **Última Actualización**: 2015-02-20 (último año disponible)

## Estructura de Archivos
- **Un archivo por año**: `Indicador--Participacion-en-el-PIB-nacional-(-)[AÑO].csv`
- **Contenido**:
  - Líneas 1-4: Metadatos del indicador
  - Línea 5: Encabezado (vacío)
  - Líneas 6-: Datos por departamento/región
  - Últimas 3 líneas: Fuente y observaciones

## Variables Clave
- **Departamentos**:
  - 19 departamentos oficiales
  - 6 regiones agregadas
- **Participación PIB**:
  - Porcentaje del PIB nacional
  - Rango: 0.73% (Flores) - 50.49% (Montevideo)
  - Suma total: 100% ± 0.01% (redondeo)

## Procesamiento Requerido
1. **Consolidación temporal**:
   - Combinar archivos anuales en serie panel
   - Normalizar nombres de departamentos
   - Eliminar agregaciones regionales redundantes

2. **Ajustes metodológicos**:
   - Unificar formato decimal (coma → punto)
   - Verificar consistencia de totales
   - Mapear a códigos ISO 3166-2:UY
