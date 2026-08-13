import json
import os
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)

AZUL_OSCURO = "#1F4E78"
AZUL_MEDIO = "#2E75B6"
AZUL_CLARO = "#DDEBF7"
ROJO = "#C0504D"
VERDE = "#4F8A5B"
GRIS = "#666666"

df = pd.read_csv("reviews_analizadas.csv")
with open("resumen_temas.json", encoding="utf-8") as f:
    resumen_temas = json.load(f)  # [[tema, cant, rating_prom], ...]

rating_prom_general = df["Rating"].mean()
total_reviews = len(df)
dist_sentimiento = df["Sentimiento"].value_counts()

# --- Gráfico 1: distribución de sentimiento ---
fig, ax = plt.subplots(figsize=(4.5, 4))
colores_sent = {"Positivo": VERDE, "Neutro": "#BBBBBB", "Negativo": ROJO}
labels = dist_sentimiento.index.tolist()
vals = dist_sentimiento.values.tolist()
cols = [colores_sent[l] for l in labels]
ax.pie(vals, labels=labels, autopct="%1.0f%%", colors=cols, textprops={"fontsize": 9})
ax.set_title("Distribución de sentimiento", fontsize=12, fontweight="bold", color=AZUL_OSCURO)
fig.tight_layout()
fig.savefig("g_sentimiento.png", dpi=150)
plt.close(fig)

# --- Gráfico 2: menciones por tema, coloreado por rating promedio ---
resumen_temas_sorted = sorted(resumen_temas, key=lambda x: x[1])
temas = [t[0] for t in resumen_temas_sorted]
menciones = [t[1] for t in resumen_temas_sorted]
ratings = [t[2] for t in resumen_temas_sorted]


def color_por_rating(r):
    if r < 3.2:
        return ROJO
    elif r < 3.8:
        return "#E0A030"
    return VERDE


colores_barras = [color_por_rating(r) for r in ratings]
fig, ax = plt.subplots(figsize=(7, 3.5))
bars = ax.barh(temas, menciones, color=colores_barras)
for bar, rating in zip(bars, ratings):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"★ {rating:.1f}", va="center", fontsize=8, color=GRIS)
ax.set_title("Menciones por tema (color = rating promedio: rojo=bajo, verde=alto)",
             fontsize=10, fontweight="bold", color=AZUL_OSCURO, loc="left")
ax.set_xlabel("Cantidad de menciones")
fig.tight_layout()
fig.savefig("g_temas.png", dpi=150)
plt.close(fig)

# --- Gráfico 3: distribución de ratings ---
fig, ax = plt.subplots(figsize=(7, 2.8))
conteo_rating = df["Rating"].value_counts().sort_index()
colores_rating = [color_por_rating(r) if r >= 3 else ROJO for r in conteo_rating.index]
ax.bar(conteo_rating.index.astype(str), conteo_rating.values, color=AZUL_MEDIO)
ax.set_title("Distribución de calificaciones (1 a 5 estrellas)", fontsize=11,
             fontweight="bold", color=AZUL_OSCURO, loc="left")
fig.tight_layout()
fig.savefig("g_ratings.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloReporte", fontSize=20, textColor=colors.HexColor(AZUL_OSCURO),
                           fontName="Helvetica-Bold", spaceAfter=10, leading=24))
styles.add(ParagraphStyle(name="Subtitulo", fontSize=10, textColor=colors.HexColor(GRIS),
                           fontName="Helvetica-Oblique", spaceAfter=16))
styles.add(ParagraphStyle(name="Seccion", fontSize=13, textColor=colors.HexColor(AZUL_OSCURO),
                           fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="Cuerpo", fontSize=10, leading=14))

story = []
story.append(Paragraph("Análisis de opiniones de clientes — Estilo Urbano", styles["TituloReporte"]))
story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y')} · {total_reviews} reviews analizadas "
                        "(Google Reviews, Instagram y formulario post-compra)", styles["Subtitulo"]))

kpi_data = [
    ["Rating promedio", "Reviews positivas", "Reviews negativas", "Total analizadas"],
    [f"{rating_prom_general:.2f} / 5",
     f"{dist_sentimiento.get('Positivo', 0)} ({dist_sentimiento.get('Positivo', 0)/total_reviews*100:.0f}%)",
     f"{dist_sentimiento.get('Negativo', 0)} ({dist_sentimiento.get('Negativo', 0)/total_reviews*100:.0f}%)",
     f"{total_reviews}"],
]
kpi_table = Table(kpi_data, colWidths=[4.2 * cm] * 4)
kpi_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(AZUL_OSCURO)),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 9),
    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor(AZUL_CLARO)),
    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 1), (-1, 1), 12),
    ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor(AZUL_OSCURO)),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
]))
story.append(kpi_table)
story.append(Spacer(1, 12))

peor_tema = min(resumen_temas, key=lambda t: t[2])
story.append(Paragraph(
    f"<b>Principal punto de atención:</b> <b>{peor_tema[0]}</b> es el tema con más quejas asociadas "
    f"({peor_tema[1]} menciones, rating promedio {peor_tema[2]:.2f}/5). Resolverlo es lo que más "
    f"impacto tendría en la satisfacción general.",
    styles["Cuerpo"]))

story.append(Paragraph("Sentimiento y calificaciones", styles["Seccion"]))
img1 = Image("g_sentimiento.png", width=8 * cm, height=8 * cm * (4 / 4.5))
img3 = Image("g_ratings.png", width=8 * cm, height=8 * cm * (2.8 / 7))
tabla_imgs = Table([[img1, img3]], colWidths=[8 * cm, 8 * cm])
tabla_imgs.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story.append(tabla_imgs)

story.append(Paragraph("¿De qué hablan los clientes?", styles["Seccion"]))
story.append(Image("g_temas.png", width=16 * cm, height=16 * cm * (3.5 / 7)))

story.append(Spacer(1, 10))
story.append(Paragraph(
    "Metodología: clasificación de sentimiento por léxico en español (palabras positivas/negativas) "
    "y detección de temas por palabras clave sobre cada comentario. Es un análisis liviano y explicable, "
    "pensado para dar una primera lectura rápida — para decisiones de mayor impacto se recomienda revisar "
    "manualmente los comentarios del tema con más quejas.",
    styles["Subtitulo"]))

doc = SimpleDocTemplate("reporte_reviews.pdf", pagesize=A4,
                         topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                         leftMargin=1.8 * cm, rightMargin=1.8 * cm)
doc.build(story)
print("Reporte generado: reporte_reviews.pdf")
