# Límites Departamentales de Uruguay

## Fuente Original
- **Proveedor**: Instituto Nacional de Estadística (INE)
- **Versión**: Censos 2011
- **Método de Obtención**: Descarga desde portal INE
- **Última Actualización**: 2011-12-01

## Estructura del Dataset
- **Formato**: Shapefile (ESRI)
- **Componentes**:
  - Polígonos departamentales (.shp)
  - Atributos geográficos (.dbf)
  - Índices espaciales (.shx, .sbn)
  - Metadatos técnicos (.pdf)

## Variables Clave
- **Cobertura**: 19 departamentos
- **Sistema de Coordenadas**: UTM 21S (EPSG:32721)
- **Precisión**: Escala 1:50.000
- **Atributos**:
  - Códigos INE e ISO
  - Medidas geométricas oficiales

## Procesamiento Requerido
1. **Transformaciones geográficas**:
   - Conversión a WGS84 geográfico (EPSG:4326)
   - Simplificación topológica para visualización web
   - Unificación con códigos de otras series

2. **Validación de datos**:
   - Chequear integridad de polígonos
   - Verificar consistencia de atributos
   - Corregir posibles solapamientos


**Nota**: Los datos deben citarse como "Fuente: INE - Censos 2011" en cualquier producto derivado