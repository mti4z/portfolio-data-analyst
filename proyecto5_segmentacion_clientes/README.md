# Segmentación de clientes con Machine Learning (RFM + K-Means)

## El problema

Todo negocio con clientes recurrentes se hace la misma pregunta: ¿a quién le doy prioridad?
Tratar a todos los clientes igual desperdicia recursos — un beneficio pensado para retener a un
cliente VIP no tiene sentido gastarlo en alguien que ya dejó de comprar hace meses, y viceversa.

## La solución

Este proyecto usa un algoritmo real de Machine Learning (K-Means) para agrupar automáticamente
a los clientes según su comportamiento de compra, sin reglas armadas a mano. El resultado es
un mapa claro de a quién priorizar, a quién recuperar, y a quién mantener activo.

## Cómo funciona (resumen técnico)

1. **RFM**: por cada cliente se calculan 3 métricas — Recencia (hace cuánto no compra),
   Frecuencia (cuántas veces compró) y Monto (cuánto gastó en total).
2. **Selección de k**: en vez de elegir a ojo cuántos segmentos armar, se prueban varias opciones
   (de 2 a 6) y se elige la que mejor separa a los clientes entre sí, usando el coeficiente de silueta.
3. **K-Means**: algoritmo de clustering que agrupa a los clientes según sus métricas RFM.
4. **Interpretación de negocio**: cada cluster se nombra según su perfil (VIP, Frecuente, Regular,
   En riesgo) y se traduce en una recomendación de acción concreta.

## Resultado

Con 20 clientes analizados se identificaron 4 segmentos:
- **VIP** (7 clientes): compran seguido y gastan más — priorizarlos con beneficios exclusivos.
- **Regular** (10 clientes): base sólida, candidatos a subir de categoría con más comunicación.
- **En riesgo — alto valor** (1 cliente): gastaba mucho y dejó de comprar — prioridad de recuperación.
- **En riesgo — bajo valor** (2 clientes): también inactivos, pero de menor impacto si se pierden.

## Por qué es valioso como servicio

- Es Machine Learning real (no solo fórmulas ni reglas fijas), demostrando manejo de librerías
  como scikit-learn.
- El resultado es 100% accionable: se puede entregar la lista de clientes por segmento para
  usar directamente en una campaña de WhatsApp/email/Instagram.
- Se adapta a cualquier negocio con historial de compras por cliente (no solo retail).

## Archivos

- `segmentacion_clientes.py` — cálculo de RFM y clustering.
- `generar_reporte_segmentacion.py` — genera los gráficos y el PDF final.
- `clientes_segmentados.csv` — listado de clientes con su segmento asignado (el entregable
  más importante para el cliente real).
- `reporte_segmentacion.pdf` — reporte visual con interpretación y recomendaciones de negocio.
