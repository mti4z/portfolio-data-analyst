"""
Generador automático de reporte de ventas
==========================================
Uso:
    python generar_reporte_automatico.py --input ventas.csv --negocio "Mi Tienda" --output reporte.pdf

Este script reemplaza el trabajo manual de: abrir el Excel de ventas, armar tablas dinámicas,
copiar gráficos a un Word/PowerPoint y mandarlo por mail cada semana/mes. Con este script,
ese proceso se reduce a un solo comando (o un doble clic si se empaqueta en un .bat/.sh).

Requiere un CSV con, como mínimo, las columnas: Fecha, Producto, Categoría, Cantidad, Total.
"""

import argparse
import os
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)

# ---------------------------------------------------------------------------
# Paleta y estilos
# ---------------------------------------------------------------------------
AZUL_OSCURO = "#1F4E78"
AZUL_MEDIO = "#2E75B6"
AZUL_CLARO = "#DDEBF7"
GRIS = "#666666"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#CCCCCC",
    "axes.grid": True,
    "grid.color": "#EAEAEA",
    "grid.linewidth": 0.6,
})


def cargar_datos(path):
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path, parse_dates=["Fecha"])
    else:
        df = pd.read_excel(path, sheet_name="Datos", parse_dates=["Fecha"])
    columnas_requeridas = {"Fecha", "Producto", "Categoría", "Cantidad", "Total"}
    faltantes = columnas_requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el archivo de entrada: {faltantes}")
    df["Mes"] = df["Fecha"].dt.to_period("M")
    return df


def fmt_money(x, pos=None):
    return f"${x:,.0f}".replace(",", ".")


def grafico_ventas_por_mes(df, out_path):
    resumen = df.groupby("Mes")["Total"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    etiquetas = [p.strftime("%b %y") for p in resumen.index]
    ax.bar(etiquetas, resumen.values, color=AZUL_MEDIO)
    ax.set_title("Ventas por mes", fontsize=12, fontweight="bold", color=AZUL_OSCURO, loc="left")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    plt.xticks(rotation=45, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def grafico_top_productos(df, out_path, top_n=8):
    resumen = df.groupby("Producto")["Total"].sum().sort_values(ascending=True).tail(top_n)
    fig, ax = plt.subplots(figsize=(7.5, 3.5))
    ax.barh(resumen.index, resumen.values, color=AZUL_OSCURO)
    ax.set_title(f"Top {top_n} productos por ventas", fontsize=12, fontweight="bold", color=AZUL_OSCURO, loc="left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def grafico_categorias(df, out_path):
    resumen = df.groupby("Categoría")["Total"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(5, 4))
    colores = plt.cm.Blues_r([i / len(resumen) * 0.7 for i in range(len(resumen))])
    ax.pie(resumen.values, labels=resumen.index, autopct="%1.0f%%",
           colors=colores, textprops={"fontsize": 8})
    ax.set_title("Ventas por categoría", fontsize=12, fontweight="bold", color=AZUL_OSCURO)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def construir_pdf(df, negocio, output_path, dir_tmp):
    ventas_totales = df["Total"].sum()
    cant_ventas = len(df)
    ticket_prom = ventas_totales / cant_ventas if cant_ventas else 0
    unidades = df["Cantidad"].sum()
    mejor_mes = df.groupby("Mes")["Total"].sum().idxmax()
    top_producto = df.groupby("Producto")["Total"].sum().idxmax()

    meses_es = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
    mejor_mes_txt = f"{meses_es[mejor_mes.month]} de {mejor_mes.year}"

    g1 = os.path.join(dir_tmp, "g1.png")
    g2 = os.path.join(dir_tmp, "g2.png")
    g3 = os.path.join(dir_tmp, "g3.png")
    grafico_ventas_por_mes(df, g1)
    grafico_top_productos(df, g2)
    grafico_categorias(df, g3)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TituloReporte", fontSize=20, textColor=colors.HexColor(AZUL_OSCURO),
                               fontName="Helvetica-Bold", spaceAfter=10, leading=24))
    styles.add(ParagraphStyle(name="Subtitulo", fontSize=10, textColor=colors.HexColor(GRIS),
                               fontName="Helvetica-Oblique", spaceAfter=16))
    styles.add(ParagraphStyle(name="Seccion", fontSize=13, textColor=colors.HexColor(AZUL_OSCURO),
                               fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="Cuerpo", fontSize=10, leading=14))

    story = []
    story.append(Paragraph(f"Reporte de ventas — {negocio}", styles["TituloReporte"]))
    story.append(Paragraph(f"Generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
                            f"Período: {df['Fecha'].min().strftime('%d/%m/%Y')} a {df['Fecha'].max().strftime('%d/%m/%Y')}",
                            styles["Subtitulo"]))

    # --- Tabla de KPIs ---
    kpi_data = [
        ["Ventas totales", "Cant. de ventas", "Ticket promedio", "Unidades vendidas"],
        [fmt_money(ventas_totales), f"{cant_ventas:,}".replace(",", "."),
         fmt_money(ticket_prom), f"{unidades:,}".replace(",", ".")],
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
    story.append(Paragraph(
        f"<b>Resumen:</b> el mejor mes fue <b>{mejor_mes_txt}</b> "
        f"y el producto más vendido fue <b>{top_producto}</b>.",
        styles["Cuerpo"]))

    story.append(Paragraph("Evolución de ventas", styles["Seccion"]))
    story.append(Image(g1, width=16 * cm, height=16 * cm * (3.2 / 7.5)))

    story.append(Paragraph("Productos y categorías", styles["Seccion"]))
    story.append(Image(g2, width=16 * cm, height=16 * cm * (3.5 / 7.5)))
    story.append(Spacer(1, 6))
    story.append(Image(g3, width=10 * cm, height=10 * cm * (4 / 5)))

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Este reporte se generó automáticamente a partir de los datos crudos de ventas. "
        "No requiere armado manual: basta con reemplazar el archivo de origen y volver a "
        "ejecutar el script para tener el reporte del período actualizado.",
        styles["Subtitulo"]))

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    doc.build(story)


def main():
    parser = argparse.ArgumentParser(description="Genera un reporte PDF automático de ventas.")
    parser.add_argument("--input", required=True, help="Archivo CSV o XLSX con los datos de ventas")
    parser.add_argument("--negocio", default="Mi Negocio", help="Nombre del negocio a mostrar en el reporte")
    parser.add_argument("--output", default="reporte_ventas.pdf", help="Nombre del PDF de salida")
    args = parser.parse_args()

    df = cargar_datos(args.input)
    dir_tmp = os.path.dirname(os.path.abspath(args.output)) or "."
    construir_pdf(df, args.negocio, args.output, dir_tmp)
    print(f"Reporte generado: {args.output}")


if __name__ == "__main__":
    main()
