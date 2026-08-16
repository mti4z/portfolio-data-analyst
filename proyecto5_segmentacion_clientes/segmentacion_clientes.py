"""
Segmentación de clientes (RFM + K-Means)
==========================================
Convierte el historial de ventas en 3 métricas por cliente (RFM):
  - Recencia:    hace cuántos días compró por última vez
  - Frecuencia:  cuántas veces compró
  - Monto:       cuánto gastó en total

Y usa un algoritmo de Machine Learning (K-Means) para agrupar a los clientes en
segmentos automáticamente, sin reglas fijas armadas a mano. El resultado responde
la pregunta que todo negocio se hace: "¿quiénes son mis mejores clientes, y a quiénes
tengo que recuperar antes de que se vayan?"
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# ---------------------------------------------------------------------------
# 1. Carga y cálculo de RFM
# ---------------------------------------------------------------------------
df = pd.read_csv("ventas.csv", parse_dates=["Fecha"])

# Excluimos "Consumidor Final": son ventas sin identificar al cliente real,
# no tiene sentido segmentar a un cliente que no podemos distinguir de otro.
df = df[df["Cliente"] != "Consumidor Final"].copy()

fecha_referencia = df["Fecha"].max() + pd.Timedelta(days=1)

rfm = df.groupby("Cliente").agg(
    Recencia=("Fecha", lambda x: (fecha_referencia - x.max()).days),
    Frecuencia=("ID Venta", "count"),
    Monto=("Total", "sum"),
).reset_index()

print("=" * 70)
print("TABLA RFM (primeras filas)")
print("=" * 70)
print(rfm.sort_values("Monto", ascending=False).head(8).to_string(index=False))
print(f"\nTotal de clientes a segmentar: {len(rfm)}")

# ---------------------------------------------------------------------------
# 2. Estandarizar y elegir la cantidad óptima de clusters (método del codo +
#    coeficiente de silueta, para no elegir "k" a ojo)
# ---------------------------------------------------------------------------
X = rfm[["Recencia", "Frecuencia", "Monto"]].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

inercias = []
siluetas = []
rango_k = range(2, 7)
for k in rango_k:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inercias.append(km.inertia_)
    siluetas.append(silhouette_score(X_scaled, labels))

print("\n" + "=" * 70)
print("SELECCIÓN DE K (cantidad de segmentos)")
print("=" * 70)
for k, inercia, sil in zip(rango_k, inercias, siluetas):
    print(f"k={k}  inercia={inercia:8.1f}  silueta={sil:.3f}")

mejor_k = rango_k[int(np.argmax(siluetas))]
print(f"\nMejor k según coeficiente de silueta: {mejor_k}")

# ---------------------------------------------------------------------------
# 3. Entrenar K-Means final con el k elegido
# ---------------------------------------------------------------------------
kmeans_final = KMeans(n_clusters=mejor_k, random_state=42, n_init=10)
rfm["Cluster"] = kmeans_final.fit_predict(X_scaled)

# ---------------------------------------------------------------------------
# 4. Interpretar y nombrar los segmentos (esto es lo que un cliente entiende,
#    no el número de cluster crudo)
# ---------------------------------------------------------------------------
perfil = rfm.groupby("Cluster")[["Recencia", "Frecuencia", "Monto"]].mean()
perfil["Cantidad de clientes"] = rfm.groupby("Cluster").size()

print("\n" + "=" * 70)
print("PERFIL DE CADA CLUSTER (promedios)")
print("=" * 70)
print(perfil.round(1).to_string())


def nombrar_segmento(row, medianas):
    alto_monto = row["Monto"] >= medianas["Monto"]
    reciente = row["Recencia"] <= medianas["Recencia"]
    frecuente = row["Frecuencia"] >= medianas["Frecuencia"]

    if alto_monto and reciente:
        return "VIP"
    elif not reciente and alto_monto:
        return "En riesgo (alto valor)"
    elif not reciente and not alto_monto:
        return "En riesgo (bajo valor)"
    elif frecuente:
        return "Frecuente"
    else:
        return "Regular"


medianas = perfil[["Recencia", "Frecuencia", "Monto"]].median()
usados = {c: nombrar_segmento(perfil.loc[c], medianas) for c in perfil.index}
rfm["Segmento"] = rfm["Cluster"].map(usados)

print("\n" + "=" * 70)
print("SEGMENTOS FINALES")
print("=" * 70)
for cluster, nombre in usados.items():
    fila = perfil.loc[cluster]
    print(f"Cluster {cluster} -> \"{nombre}\": {int(fila['Cantidad de clientes'])} clientes, "
          f"recencia prom. {fila['Recencia']:.0f} días, frecuencia prom. {fila['Frecuencia']:.1f} compras, "
          f"monto prom. ${fila['Monto']:,.0f}")

# ---------------------------------------------------------------------------
# 5. Exportar resultados
# ---------------------------------------------------------------------------
rfm_export = rfm.sort_values(["Segmento", "Monto"], ascending=[True, False])
rfm_export.to_csv("clientes_segmentados.csv", index=False)

import json
resumen = {
    "mejor_k": int(mejor_k),
    "rango_k": list(rango_k),
    "inercias": inercias,
    "siluetas": siluetas,
    "perfil": perfil.reset_index().to_dict(orient="records"),
    "nombres": {str(k): v for k, v in usados.items()},
}
with open("resumen_clustering.json", "w", encoding="utf-8") as f:
    json.dump(resumen, f, default=str)

# Guardar también los datos con features escalados, para graficar después
rfm.to_pickle("rfm_completo.pkl")

print("\nArchivos generados: clientes_segmentados.csv, resumen_clustering.json, rfm_completo.pkl")
