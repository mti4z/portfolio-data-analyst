"""
Análisis de opiniones de clientes (reviews)
=============================================
Toma un CSV de reviews (Fecha, Cliente, Producto, Rating, Comentario) y responde
las preguntas que a un dueño de negocio realmente le interesan:
  - ¿Los clientes están conformes en general?
  - ¿De qué se quejan más?
  - ¿Qué es lo que más destacan?

No depende de librerías de NLP pesadas ni de internet: usa un léxico de palabras
en español armado a mano (positivo/negativo) y detección de temas por palabras clave.
Esto lo hace liviano, explicable y fácil de ajustar para otro rubro.
"""

import re
import unicodedata
from collections import Counter, defaultdict

import pandas as pd

# ---------------------------------------------------------------------------
# 1. Carga
# ---------------------------------------------------------------------------
df = pd.read_csv("reviews_clientes.csv")


def quitar_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def tokenizar(texto):
    texto = quitar_acentos(texto.lower())
    return re.findall(r"[a-záéíóúñ]+", texto)


# ---------------------------------------------------------------------------
# 2. Léxico de sentimiento en español (armado a mano para este dominio)
# ---------------------------------------------------------------------------
PALABRAS_POSITIVAS = {
    "excelente", "perfecto", "genial", "hermoso", "buena", "bueno", "rapido", "rapidisimo",
    "conforme", "recomiendo", "mejor", "increible", "espectacular", "correcto", "justo",
    "encanto", "encanta", "feliz", "contenta", "contento", "vale", "calzo", "calzaron", "superó", "supero",
}
PALABRAS_NEGATIVAS = {
    "chico", "chica", "mal", "mala", "malo", "tardo", "tardaron", "incompleto", "roto",
    "rota", "mancha", "carisimo", "caro", "decepcionada", "decepcionado", "destiño", "destino",
    "destejer", "nunca", "faltaba", "reembolso", "problema", "peor", "lento", "lenta", "no",
}

NEGACIONES = {"no", "nunca", "tampoco"}


def puntaje_sentimiento(texto):
    tokens = tokenizar(texto)
    score = 0
    for i, tok in enumerate(tokens):
        negado = i > 0 and tokens[i - 1] in NEGACIONES
        if tok in PALABRAS_POSITIVAS:
            score += -1 if negado else 1
        elif tok in PALABRAS_NEGATIVAS and tok != "no":
            score += 1 if negado else -1
    return score


def clasificar_sentimiento(score):
    if score > 0:
        return "Positivo"
    elif score < 0:
        return "Negativo"
    return "Neutro"


df["_score"] = df["Comentario"].apply(puntaje_sentimiento)
df["Sentimiento"] = df["_score"].apply(clasificar_sentimiento)

# ---------------------------------------------------------------------------
# 3. Detección de temas por palabras clave
# ---------------------------------------------------------------------------
TEMAS = {
    "Talles": {"talle", "talles", "chico", "chica", "grande", "ajustado", "calzo", "calzaron"},
    "Calidad": {"calidad", "tela", "destiño", "destino", "lavada", "lavo", "deformo", "destejer"},
    "Envío": {"envio", "envío", "llego", "llegó", "tardo", "tardaron", "paquete", "roto", "rota",
              "mancha", "incompleto", "dias", "semanas"},
    "Atención al cliente": {"atencion", "atención", "respondieron", "whatsapp", "instagram",
                             "escribi", "contestar", "ayudaron", "reembolso", "cambio"},
    "Precio": {"precio", "caro", "carisimo", "barato", "vale"},
}


def temas_mencionados(texto):
    tokens = set(tokenizar(texto))
    return [tema for tema, palabras in TEMAS.items() if tokens & palabras]


df["Temas"] = df["Comentario"].apply(temas_mencionados)

# ---------------------------------------------------------------------------
# 4. Reporte en consola
# ---------------------------------------------------------------------------
print("=" * 70)
print("RESUMEN GENERAL")
print("=" * 70)
print(f"Total de reviews analizadas: {len(df)}")
print(f"Rating promedio: {df['Rating'].mean():.2f} / 5")
print()
print("Distribución de sentimiento:")
print(df["Sentimiento"].value_counts())
print()

print("=" * 70)
print("MENCIONES POR TEMA (y rating promedio asociado)")
print("=" * 70)
conteo_temas = Counter()
rating_por_tema = defaultdict(list)
for _, row in df.iterrows():
    for tema in row["Temas"]:
        conteo_temas[tema] += 1
        rating_por_tema[tema].append(row["Rating"])

resumen_temas = []
for tema, cant in conteo_temas.most_common():
    rating_prom = sum(rating_por_tema[tema]) / len(rating_por_tema[tema])
    resumen_temas.append((tema, cant, rating_prom))
    print(f"{tema:22s} menciones: {cant:3d}   rating promedio: {rating_prom:.2f}")

print()
print("=" * 70)
print("TOP QUEJAS (temas con rating promedio más bajo, mín. 5 menciones)")
print("=" * 70)
quejas = sorted([t for t in resumen_temas if t[1] >= 5], key=lambda x: x[2])
for tema, cant, rating_prom in quejas[:3]:
    print(f"⚠ {tema}: {cant} menciones, rating promedio {rating_prom:.2f}")

# Exportar CSV con clasificación para usar en el reporte visual
df_export = df.drop(columns=["_score"])
df_export["Temas"] = df_export["Temas"].apply(lambda t: ", ".join(t) if t else "")
df_export.to_csv("reviews_analizadas.csv", index=False)

# Exportar resumen de temas para el reporte
import json
with open("resumen_temas.json", "w", encoding="utf-8") as f:
    json.dump(resumen_temas, f)

print("\nArchivos generados: reviews_analizadas.csv, resumen_temas.json")
