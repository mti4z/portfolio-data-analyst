# Automatización de reportes de ventas

## El problema

Muchos dueños de negocio (o sus empleados) arman a mano, cada semana o cada mes, el mismo
reporte: abren el Excel de ventas, arman una tabla dinámica, copian gráficos a un Word o
PowerPoint, y lo mandan por mail. Es un proceso repetitivo que consume horas y es propenso a errores.

## La solución

Un script en Python que toma el archivo crudo de ventas (CSV o Excel) y genera automáticamente
un reporte PDF ejecutivo con KPIs y gráficos — sin ningún armado manual.

## Cómo se usa

```bash
python generar_reporte_automatico.py --input ventas.csv --negocio "Nombre del Negocio" --output reporte.pdf
```

Con eso se genera un PDF de 2 páginas con:
- KPIs principales (ventas totales, cantidad de ventas, ticket promedio, unidades vendidas)
- Gráfico de evolución de ventas por mes
- Top productos por ventas
- Distribución de ventas por categoría

## Por qué es valioso como servicio

- **Se adapta a cualquier corte de datos**: se probó con el año completo y con un trimestre,
  y el script arma el reporte correcto en ambos casos sin tocar el código.
- **Reutilizable semana a semana**: el cliente solo necesita reemplazar el archivo de origen
  (por ejemplo, exportando de su sistema de ventas) y volver a correr el script.
- **Se puede empaquetar** para que el cliente ni siquiera vea código: un acceso directo o un
  botón que ejecuta el script y le abre el PDF.
- **Punto de partida para algo más grande**: este mismo esquema se puede conectar a Google
  Sheets, a una base de datos, o programarse para que se genere y se mande por mail solo,
  todos los lunes a la mañana.

## Archivos

- `generar_reporte_automatico.py` — el script.
- `ventas.csv` — ejemplo de datos de entrada (un año completo).
- `reporte_ventas.pdf` — reporte generado a partir del año completo.
- `reporte_trimestral.pdf` — el mismo script corrido sobre un subconjunto (último trimestre),
  para demostrar que se adapta a cualquier período sin cambiar el código.
