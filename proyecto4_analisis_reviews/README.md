# Análisis de opiniones de clientes (reviews)

## El problema

Las opiniones de clientes (Google Reviews, comentarios de Instagram, encuestas post-compra)
suelen quedar dispersas y sin analizar. El negocio sabe que "hay reviews", pero no tiene una
lectura clara de qué le está fallando ni qué es lo que más valoran sus clientes.

## La solución

Un análisis que clasifica automáticamente el sentimiento de cada review (positivo/negativo/neutro)
y detecta los temas más mencionados (talles, envío, calidad, atención, precio), cruzándolos con
el rating para identificar el problema con más impacto real en la satisfacción del cliente.

## Cómo funciona (resumen técnico)

- **Clasificación de sentimiento**: léxico en español armado a mano (palabras positivas/negativas),
  sin depender de librerías pesadas ni de internet — liviano y fácil de ajustar a otro rubro.
- **Detección de temas**: por palabras clave sobre cada comentario (talles, calidad, envío,
  atención, precio).
- **Cruce con rating**: para cada tema se calcula el rating promedio asociado, identificando
  cuál es el que más está afectando la satisfacción general.

## Resultado

Sobre 111 reviews analizadas: rating promedio 3.39/5, con **Envío** identificado como el
principal punto de fricción (37 menciones, rating promedio 3.08) — el tipo de insight que le
permite a un negocio priorizar en qué mejorar primero, en vez de adivinar.

## Por qué es valioso como servicio

- Convierte texto no estructurado (opiniones sueltas) en información accionable.
- No requiere que el cliente tenga sus reviews ordenadas de antemano.
- El mismo enfoque se adapta a cualquier rubro con solo ajustar el diccionario de temas.

## Archivos

- `analizar_reviews.py` — clasificación de sentimiento y detección de temas.
- `generar_reporte_reviews.py` — genera los gráficos y el PDF final.
- `reviews_clientes.csv` — dataset original de reviews.
- `reviews_analizadas.csv` — reviews con sentimiento y temas ya clasificados.
- `reporte_reviews.pdf` — reporte visual con los insights y recomendaciones.
