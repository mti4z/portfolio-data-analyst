"""
Limpieza de base de datos de clientes
======================================
Problema típico de pyme: una base de clientes cargada manualmente (Excel, formularios,
carga telefónica) durante meses/años, con inconsistencias que impiden analizarla o
usarla para marketing/facturación con confianza.

Este script toma clientes_sucio.csv y entrega clientes_limpio.csv, documentando
cada paso y su impacto.
"""

import pandas as pd
import re

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

# ---------------------------------------------------------------------------
# 1. Carga y diagnóstico inicial
# ---------------------------------------------------------------------------
df = pd.read_csv("clientes_sucio.csv", dtype=str)
filas_iniciales = len(df)

print("=" * 70)
print("DIAGNÓSTICO INICIAL")
print("=" * 70)
print(f"Filas totales: {filas_iniciales}")
print(f"Columnas: {list(df.columns)}")
print(f"Valores nulos/vacíos por columna:")
print((df.isna() | (df.apply(lambda col: col.str.strip() == ""))).sum())

# ---------------------------------------------------------------------------
# 2. Eliminar filas basura (sin nombre real o placeholders tipo "test", "-")
# ---------------------------------------------------------------------------
placeholders_invalidos = {"", "-", "test", "n/a", "nan"}
df["Nombre"] = df["Nombre"].fillna("").str.strip()
mask_basura = df["Nombre"].str.lower().isin(placeholders_invalidos)
filas_basura = mask_basura.sum()
df = df[~mask_basura].copy()

# ---------------------------------------------------------------------------
# 3. Normalizar texto: espacios, mayúsculas/minúsculas consistentes (Title Case)
# ---------------------------------------------------------------------------
def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    valor = re.sub(r"\s+", " ", str(valor)).strip()
    return valor

df["Nombre"] = df["Nombre"].apply(limpiar_texto).str.title()
df["Ciudad"] = df["Ciudad"].apply(limpiar_texto)

# ---------------------------------------------------------------------------
# 4. Estandarizar ciudades (mapeo de variantes a un valor canónico)
# ---------------------------------------------------------------------------
mapeo_ciudades = {
    "caba": "CABA", "capital federal": "CABA", "c.a.b.a.": "CABA",
    "bs as capital": "CABA", "buenos aires (caba)": "CABA",
    "quilmes": "Quilmes", "quilmes bs as": "Quilmes",
    "la plata": "La Plata", "la plata, ba": "La Plata",
    "avellaneda": "Avellaneda",
    "san isidro": "San Isidro",
}
df["Ciudad"] = df["Ciudad"].str.lower().map(mapeo_ciudades).fillna(df["Ciudad"])

# ---------------------------------------------------------------------------
# 5. Validar y limpiar emails
# ---------------------------------------------------------------------------
patron_email = re.compile(r"^[\w.\-ñáéíóú]+@[\w\-]+\.[a-z.]+$", re.IGNORECASE)

def limpiar_email(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor).strip().lower()
    return valor if patron_email.match(valor) else ""

df["Email"] = df["Email"].apply(limpiar_email)
emails_invalidos = (df["Email"] == "").sum()

# ---------------------------------------------------------------------------
# 6. Normalizar teléfonos a un formato único: 11XXXXXXXX (10 dígitos, AMBA)
# ---------------------------------------------------------------------------
def limpiar_telefono(valor):
    if pd.isna(valor):
        return ""
    digitos = re.sub(r"\D", "", str(valor))
    # Quitar código de país si está presente (54)
    if digitos.startswith("54") and len(digitos) > 10:
        digitos = digitos[2:]
    # Quitar el 0 inicial del código de área largo, ej "(011) 4000-1234" -> "0114000..."
    if digitos.startswith("0") and len(digitos) == 11:
        digitos = digitos[1:]
    if len(digitos) == 10 and digitos.startswith("11"):
        return f"{digitos[:2]}-{digitos[2:6]}-{digitos[6:]}"
    return ""  # no confiable / incompleto

df["Teléfono"] = df["Teléfono"].apply(limpiar_telefono)
telefonos_invalidos = (df["Teléfono"] == "").sum()

# ---------------------------------------------------------------------------
# 7. Normalizar fechas (múltiples formatos -> ISO YYYY-MM-DD)
# ---------------------------------------------------------------------------
def limpiar_fecha(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return pd.NaT
    valor = str(valor).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return pd.to_datetime(valor, format=fmt)
        except ValueError:
            continue
    return pd.NaT

df["Fecha de Alta"] = df["Fecha de Alta"].apply(limpiar_fecha)
fechas_invalidas = df["Fecha de Alta"].isna().sum()

# ---------------------------------------------------------------------------
# 8. Normalizar "Compras Totales" a numérico
# ---------------------------------------------------------------------------
df["Compras Totales"] = pd.to_numeric(df["Compras Totales"], errors="coerce").fillna(0).astype(int)

# ---------------------------------------------------------------------------
# 9. Eliminar duplicados (mismo cliente cargado más de una vez)
#    Criterio: mismo nombre normalizado + misma ciudad -> nos quedamos con el
#    registro que tenga más datos completos (email y teléfono válidos)
# ---------------------------------------------------------------------------
df["_completitud"] = (df["Email"] != "").astype(int) + (df["Teléfono"] != "").astype(int)
df = df.sort_values("_completitud", ascending=False)
duplicados_antes = len(df)
df = df.drop_duplicates(subset=["Nombre", "Ciudad"], keep="first")
duplicados_eliminados = duplicados_antes - len(df)
df = df.drop(columns=["_completitud"])

# ---------------------------------------------------------------------------
# 10. Orden final y export
# ---------------------------------------------------------------------------
df = df.sort_values("Nombre").reset_index(drop=True)
df["Fecha de Alta"] = df["Fecha de Alta"].dt.strftime("%Y-%m-%d")
df.to_csv("clientes_limpio.csv", index=False)

# ---------------------------------------------------------------------------
# Resumen final
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("RESUMEN DE LIMPIEZA")
print("=" * 70)
print(f"Filas iniciales:              {filas_iniciales}")
print(f"Filas basura eliminadas:      {filas_basura}")
print(f"Duplicados eliminados:        {duplicados_eliminados}")
print(f"Filas finales:                {len(df)}")
print(f"Emails inválidos/faltantes:   {emails_invalidos} (marcados vacíos, no inventados)")
print(f"Teléfonos inválidos/faltantes:{telefonos_invalidos} (marcados vacíos, no inventados)")
print(f"Fechas no reconocidas:        {fechas_invalidas}")
print()
print("Muestra del resultado limpio:")
print(df.head(8).to_string(index=False))
