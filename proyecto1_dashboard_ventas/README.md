# Dashboard de ventas — Tienda de ropa

## El problema

La mayoría de las pymes tienen sus ventas registradas en algún lado (un sistema de facturación,
un cuaderno, planillas sueltas) pero no tienen forma rápida de responder preguntas simples:
¿cuánto vendí este mes vs el anterior?, ¿qué productos son los que más se venden?, ¿quiénes son
mis mejores clientes?

## La solución

Un dashboard en Excel que toma los datos crudos de ventas (1.695 registros de un año) y muestra
automáticamente los indicadores clave: ventas totales, ticket promedio, evolución mensual, top
productos, ventas por categoría, top clientes y ventas por canal (local / Instagram / WhatsApp).

## Por qué es valioso como servicio

- **Todo son fórmulas reales** (SUMIFS, COUNTIFS, INDEX/MATCH), no números pegados a mano.
  Si el cliente agrega filas nuevas a la hoja de Datos, el dashboard entero se actualiza solo.
- **No requiere que el cliente sepa Excel avanzado**: solo carga sus ventas en el formato de la
  hoja "Datos" y el dashboard ya está listo.
- **Es la puerta de entrada a servicios más grandes**: automatización de reportes (ver proyecto 3)
  y análisis más profundos con Python.

## Archivos

- `dashboard_ventas_tienda_ropa.xlsx` — el archivo completo, con la hoja "Datos" (1.695 filas)
  y la hoja "Dashboard" con KPIs y gráficos.
