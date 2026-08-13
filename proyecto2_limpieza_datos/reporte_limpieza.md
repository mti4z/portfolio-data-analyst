# Limpieza de base de datos de clientes — Caso práctico

## El problema

Muchas pymes acumulan su base de clientes cargándola a mano durante meses o años:
un empleado la carga en un formulario, otro en una planilla, otro por teléfono.
El resultado casi siempre es el mismo: **datos que no se pueden usar con confianza**
para facturar, hacer marketing o simplemente saber cuántos clientes reales tiene el negocio.

Este proyecto simula ese escenario: una base de **52 registros** con los problemas típicos
que aparecen en cualquier carga manual.

## Problemas detectados

| Problema | Ejemplo encontrado |
|---|---|
| Nombres con mayúsculas/minúsculas inconsistentes | `MARIA GONZALEZ`, `maria gonzalez`, `  María González  ` |
| Ciudades escritas de formas distintas | `CABA`, `Capital Federal`, `C.A.B.A.`, `Bs As Capital` |
| Teléfonos en formatos distintos | `11-4000-1234`, `(011) 4000-1234`, `1140001234` |
| Emails inválidos o vacíos | `sin_arroba`, `nombre@@gmail`, campos en blanco |
| Fechas en formatos mezclados | `26/12/2025`, `2025-12-26`, `26-12-2025` |
| Clientes duplicados | La misma persona cargada 2 o 3 veces con variaciones |
| Filas basura | Registros vacíos o con texto tipo `test`, `-` |

## Proceso de limpieza

1. **Diagnóstico**: medir cuántos valores faltan o son inválidos por columna, antes de tocar nada.
2. **Eliminar filas basura**: registros sin nombre real o con placeholders.
3. **Normalizar texto**: espacios dobles, mayúsculas/minúsculas, a un formato consistente (Nombre Propio).
4. **Estandarizar ciudades**: mapear todas las variantes a un único valor canónico.
5. **Validar emails**: con una expresión regular, separando los válidos de los que no sirven (no se inventan datos).
6. **Normalizar teléfonos**: a un único formato `11-XXXX-XXXX`, descartando los que no se pueden reconstruir con confianza.
7. **Unificar fechas**: de 3 formatos distintos a un único estándar ISO (`AAAA-MM-DD`).
8. **Eliminar duplicados**: detectando la misma persona cargada más de una vez, conservando siempre la versión con más datos completos.

## Resultado

| Métrica | Valor |
|---|---|
| Filas originales | 52 |
| Filas basura eliminadas | 5 |
| Clientes duplicados eliminados | 17 |
| **Clientes únicos y válidos al final** | **30** |
| Emails inválidos o faltantes identificados | 7 |
| Teléfonos inválidos o faltantes identificados | 6 |

**Nada se "inventó"**: donde el dato original no permitía reconstruir un email o teléfono
confiable, se dejó en blanco en lugar de adivinar. Esto es clave en un trabajo de limpieza
profesional — mejor un dato faltante visible que un dato falso que después genera errores.

## Impacto para un negocio real

Con esta base limpia, el negocio ahora puede:
- Saber su cantidad **real** de clientes (30, no 52).
- Enviar una campaña de WhatsApp/email sin duplicar envíos a la misma persona.
- Confiar en reportes de "clientes por ciudad" o "compras totales" sin que estén inflados por duplicados.

## Archivos de este proyecto

- `clientes_sucio.csv` — dataset original con los problemas.
- `limpieza_datos.py` — script de limpieza documentado paso a paso (Python + pandas).
- `clientes_limpio.csv` — resultado final, listo para usar.

---
*Dataset generado de forma sintética con fines demostrativos de portfolio.*
