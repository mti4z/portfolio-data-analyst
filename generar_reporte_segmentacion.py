import json

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
GRIS = "#666666"
COLOR_SEGMENTOS = {
    "VIP": "#2E7D32",
    "Frecuente": "#2E75B6",
    "Regular": "#8E9BAA",
    "En riesgo (alto valor)": "#E0A030",
    "En riesgo (bajo valor)": "#C0504D",
}

rfm = pd.read_csv("clientes_segmentados.csv")
with open("resumen_clustering.json", encoding="utf-8") as f:
    resumen = json.load(f)

# --- Gráfico 1: método del codo + silueta (justifica la elección de k) ---
fig, ax1 = plt.subplots(figsize=(7, 3.2))
ax2 = ax1.twinx()
ax1.plot(resumen["rango_k"], resumen["inercias"], "o-", color=AZUL_OSCURO, label="Inercia")
ax2.plot(resumen["rango_k"], resumen["siluetas"], "o-", color="#C0504D", label="Silueta")
ax1.set_xlabel("Cantidad de segmentos (k)")
ax1.set_ylabel("Inercia", color=AZUL_OSCURO)
ax2.set_ylabel("Coef. de silueta", color="#C0504D")
ax1.axvline(resumen["mejor_k"], color="#999999", linestyle="--", linewidth=1)
ax1.set_title(f"Selección de k = {resumen['mejor_k']} segmentos (mejor silueta)",
              fontsize=11, fontweight="bold", color=AZUL_OSCURO, loc="left")
fig.tight_layout()
fig.savefig("g_seleccion_k.png", dpi=150)
plt.close(fig)

# --- Gráfico 2: scatter Frecuencia vs Monto, coloreado por segmento ---
fig, ax = plt.subplots(figsize=(7.5, 5))
for seg, grupo in rfm.groupby("Segmento"):
    ax.scatter(grupo["Frecuencia"], grupo["Monto"], s=90,
               color=COLOR_SEGMENTOS.get(seg, "#999999"), label=seg, edgecolor="white", linewidth=0.8)
ax.set_xlabel("Frecuencia de compra (cant. de ventas)")
ax.set_ylabel("Monto total gastado ($)")
ax.set_title("Segmentos de clientes", fontsize=12, fontweight="bold", color=AZUL_OSCURO, loc="left")
ax.legend(loc="lower right", fontsize=8, framealpha=0.9)
fig.tight_layout()
fig.savefig("g_segmentos_scatter.png", dpi=150)
plt.close(fig)

# --- Gráfico 3: cantidad de clientes y monto total por segmento ---
resumen_seg = rfm.groupby("Segmento").agg(
    Clientes=("Cliente", "count"), Monto_total=("Monto", "sum")
).sort_values("Monto_total", ascending=True)
fig, ax = plt.subplots(figsize=(7.5, 3.2))
colores_barras = [COLOR_SEGMENTOS.get(s, "#999999") for s in resumen_seg.index]
bars = ax.barh(resumen_seg.index, resumen_seg["Monto_total"], color=colores_barras)
for bar, cant in zip(bars, resumen_seg["Clientes"]):
    etiqueta = "cliente" if cant == 1 else "clientes"
    ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
            f"{cant} {etiqueta}", va="center", fontsize=8, color=GRIS)
ax.set_title("Facturación total por segmento", fontsize=11, fontweight="bold", color=AZUL_OSCURO, loc="left")
ax.set_xlabel("Monto total ($)")
fig.tight_layout()
fig.savefig("g_facturacion_segmento.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# Recomendaciones de negocio por segmento (esto es lo que un cliente compra)
# ---------------------------------------------------------------------------
RECOMENDACIONES = {
    "VIP": "Son tus clientes más valiosos: compran seguido y gastan más. Priorizalos con "
           "beneficios exclusivos (acceso anticipado a nuevas colecciones, descuentos especiales) "
           "para asegurarte de que no se vayan a la competencia.",
    "Frecuente": "Compran seguido pero todavía no llegan al ticket de los VIP. Son los mejores "
                 "candidatos para técnicas de upselling: ofrecerles productos complementarios "
                 "o combos para aumentar su ticket promedio.",
    "Regular": "Base sólida de clientes que compra con cierta regularidad. Mantenerlos activos con "
               "comunicación periódica (newsletter, novedades) ayuda a que con el tiempo migren "
               "hacia el segmento Frecuente o VIP.",
    "En riesgo (alto valor)": "Fueron grandes compradores pero hace tiempo no vuelven. Son la "
                               "prioridad número uno para una campaña de recuperación (contacto "
                               "personalizado, descuento de reactivación) — perderlos duele más "
                               "que perder a cualquier otro segmento.",
    "En riesgo (bajo valor)": "Hace tiempo no compran y históricamente gastaban menos. Vale la pena "
                               "un intento de recuperación con bajo costo (email o mensaje "
                               "automático), pero no es la prioridad frente a los de alto valor.",
}

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloReporte", fontSize=20, textColor=colors.HexColor(AZUL_OSCURO),
                           fontName="Helvetica-Bold", spaceAfter=10, leading=24))
styles.add(ParagraphStyle(name="Subtitulo", fontSize=10, textColor=colors.HexColor(GRIS),
                           fontName="Helvetica-Oblique", spaceAfter=16))
styles.add(ParagraphStyle(name="Seccion", fontSize=13, textColor=colors.HexColor(AZUL_OSCURO),
                           fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="Cuerpo", fontSize=10, leading=14))
styles.add(ParagraphStyle(name="SegmentoTitulo", fontSize=11, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3))

story = []
story.append(Paragraph("Segmentación de clientes — Estilo Urbano", styles["TituloReporte"]))
story.append(Paragraph(f"Análisis RFM + Machine Learning (K-Means) sobre {len(rfm)} clientes identificados",
                        styles["Subtitulo"]))

kpi_data = [
    ["Clientes analizados", "Segmentos encontrados", "Clientes VIP", "Clientes en riesgo"],
    [str(len(rfm)), str(resumen["mejor_k"]),
     str((rfm["Segmento"] == "VIP").sum()),
     str(rfm["Segmento"].str.startswith("En riesgo").sum())],
]
kpi_table = Table(kpi_data, colWidths=[4.2 * cm] * 4)
kpi_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(AZUL_OSCURO)),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 9),
    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor(AZUL_CLARO)),
    ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 1), (-1, 1), 13),
    ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor(AZUL_OSCURO)),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
]))
story.append(kpi_table)
story.append(Spacer(1, 10))

story.append(Paragraph("¿Cómo se armaron los segmentos?", styles["Seccion"]))
story.append(Paragraph(
    "Se calcularon 3 métricas por cliente (RFM: Recencia, Frecuencia y Monto gastado) y se usó "
    "K-Means, un algoritmo de Machine Learning, para agrupar a los clientes automáticamente según "
    "su comportamiento real de compra — sin reglas fijas armadas a mano. La cantidad de segmentos "
    "no se eligió a ojo: se probaron varias opciones y se seleccionó la que mejor separa a los "
    "clientes entre sí (coeficiente de silueta).", styles["Cuerpo"]))
story.append(Image("g_seleccion_k.png", width=15 * cm, height=15 * cm * (3.2 / 7)))

story.append(Paragraph("Mapa de segmentos", styles["Seccion"]))
story.append(Image("g_segmentos_scatter.png", width=15 * cm, height=15 * cm * (5 / 7.5)))

story.append(Paragraph("Facturación por segmento", styles["Seccion"]))
story.append(Image("g_facturacion_segmento.png", width=15 * cm, height=15 * cm * (3.2 / 7.5)))

story.append(Paragraph("Qué hacer con cada segmento", styles["Seccion"]))
resumen_seg_orden = rfm.groupby("Segmento").agg(
    Clientes=("Cliente", "count"), Monto=("Monto", "mean")
).sort_values("Monto", ascending=False)
for seg in resumen_seg_orden.index:
    cant = int(resumen_seg_orden.loc[seg, "Clientes"])
    etiqueta = "cliente" if cant == 1 else "clientes"
    color_hex = COLOR_SEGMENTOS.get(seg, "#333333")
    story.append(Paragraph(f'<font color="{color_hex}">●</font> {seg} ({cant} {etiqueta})',
                            styles["SegmentoTitulo"]))
    story.append(Paragraph(RECOMENDACIONES.get(seg, ""), styles["Cuerpo"]))

story.append(Spacer(1, 12))
story.append(Paragraph(
    "Metodología: RFM (Recency, Frequency, Monetary) + K-Means sobre variables estandarizadas. "
    "Se excluyeron las ventas de 'Consumidor Final' por no poder identificar al cliente real. "
    "El listado completo cliente por cliente está disponible en clientes_segmentados.csv.",
    styles["Subtitulo"]))

doc = SimpleDocTemplate("reporte_segmentacion.pdf", pagesize=A4,
                         topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                         leftMargin=1.8 * cm, rightMargin=1.8 * cm)
doc.build(story)
print("Reporte generado: reporte_segmentacion.pdf")
