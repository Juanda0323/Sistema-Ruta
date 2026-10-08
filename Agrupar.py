
"""
Agrupar.py - Aprendizaje NO supervisado (agrupamiento)
==================================================================

Objetivo: descubrir, sin etiquetas, que TIPOS de estacion existen en el
sistema de transporte segun su perfil de demanda (cap. 16 de Palma Mendez,
2008: tecnicas de agrupamiento).

Metodos usados:
  1) K-Means: agrupa minimizando la distancia de cada punto al centro de su
     grupo. Se prueba con k = 2..8 y se elige k con el indice de silueta.
  2) Agrupamiento jerarquico aglomerativo (Ward): une grupos paso a paso;
     se dibuja el dendrograma sobre el perfil promedio de cada estacion.

Diferencia con la actividad anterior: aqui NO se le dice al algoritmo cual
es la "respuesta correcta"; el solo encuentra la estructura de los datos.

Uso:
    python Agrupar.py
(requiere haber ejecutado antes: python Generar_DataSet_Estaciones.py)
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.cluster.hierarchy import linkage, dendrogram

ARCHIVO_DATOS = "dataset_estaciones.csv"
CARPETA = "resultados_clustering"
SEMILLA = 42

# Variables usadas para agrupar (NO incluye 'arquetipo_simulado')
VARIABLES = ["pasajeros_pico_manana", "pasajeros_valle", "pasajeros_pico_tarde",
             "pasajeros_noche", "num_lineas", "num_conexiones", "proporcion_pico"]


def main():
    os.makedirs(CARPETA, exist_ok=True)
    salida = []

    def imprimir(texto=""):
        print(texto)
        salida.append(str(texto))

    # 1) Cargar y estandarizar (K-Means usa distancias: las variables deben
    #    tener la misma escala)
    df = pd.read_csv(ARCHIVO_DATOS)
    imprimir(f"Registros: {len(df)}  |  Estaciones: {df['estacion'].nunique()}")
    X = StandardScaler().fit_transform(df[VARIABLES])

    # 2) Elegir k: inercia (codo) y silueta
    imprimir("\n--- Seleccion del numero de grupos (K-Means) ---")
    ks = list(range(2, 9))
    inercias, siluetas = [], []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEMILLA).fit(X)
        inercias.append(km.inertia_)
        siluetas.append(silhouette_score(X, km.labels_))
        imprimir(f"k={k}  inercia={km.inertia_:9.1f}  silueta={siluetas[-1]:.3f}")
    k_optimo = ks[siluetas.index(max(siluetas))]
    imprimir(f"\nk elegido (mayor silueta): {k_optimo}")

    fig, ejes = plt.subplots(1, 2, figsize=(11, 4))
    ejes[0].plot(ks, inercias, "o-"); ejes[0].set_title("Metodo del codo")
    ejes[0].set_xlabel("k"); ejes[0].set_ylabel("Inercia")
    ejes[1].plot(ks, siluetas, "o-", color="green")
    ejes[1].set_title("Indice de silueta"); ejes[1].set_xlabel("k")
    plt.tight_layout(); plt.savefig(f"{CARPETA}/seleccion_k.png", dpi=120); plt.close()

    # 3) K-Means final
    km = KMeans(n_clusters=k_optimo, n_init=10, random_state=SEMILLA).fit(X)
    df["grupo_kmeans"] = km.labels_

    # 4) Jerarquico con el mismo k, para comparar
    jer = AgglomerativeClustering(n_clusters=k_optimo, linkage="ward").fit(X)
    df["grupo_jerarquico"] = jer.labels_

    imprimir("\n--- Comparacion de metodos ---")
    imprimir(f"Silueta K-Means    : {silhouette_score(X, km.labels_):.3f}")
    imprimir(f"Silueta Jerarquico : {silhouette_score(X, jer.labels_):.3f}")
    imprimir(f"Acuerdo entre ambos (ARI): "
             f"{adjusted_rand_score(df['grupo_kmeans'], df['grupo_jerarquico']):.3f}")

    # 5) Validacion externa: los grupos coinciden con la estructura oculta?
    ari = adjusted_rand_score(df["arquetipo_simulado"], df["grupo_kmeans"])
    imprimir(f"\nAcuerdo de K-Means con el arquetipo simulado (ARI): {ari:.3f}")
    imprimir("(1.0 = coincidencia perfecta; 0 = agrupacion al azar)")
    imprimir("\nTabla cruzada grupo vs arquetipo simulado:")
    imprimir(pd.crosstab(df["grupo_kmeans"], df["arquetipo_simulado"]).to_string())

    # 6) Perfil (interpretacion) de cada grupo
    perfil = df.groupby("grupo_kmeans")[VARIABLES].mean().round(2)
    perfil["n_registros"] = df.groupby("grupo_kmeans").size()
    imprimir("\n--- Perfil promedio de cada grupo ---")
    imprimir(perfil.T.to_string())
    perfil.to_csv(f"{CARPETA}/perfil_grupos.csv")

    # 7) A que grupo pertenece cada estacion
    asignacion = (df.groupby("estacion")["grupo_kmeans"]
                    .agg(lambda s: s.value_counts().idxmax()))
    pureza = (df.groupby("estacion")["grupo_kmeans"]
                .agg(lambda s: s.value_counts(normalize=True).max()))
    resumen = pd.DataFrame({"grupo": asignacion, "pureza": pureza.round(2)})
    resumen = resumen.sort_values(["grupo", "pureza"], ascending=[True, False])
    imprimir("\n--- Grupo de cada estacion (el mas frecuente en sus 60 dias) ---")
    imprimir(resumen.to_string())
    resumen.to_csv(f"{CARPETA}/estaciones_por_grupo.csv")

    # 8) Grafico PCA (2 dimensiones)
    pca = PCA(n_components=2, random_state=SEMILLA)
    P = pca.fit_transform(X)
    plt.figure(figsize=(8, 6))
    plt.scatter(P[:, 0], P[:, 1], c=km.labels_, cmap="viridis", s=18, alpha=0.7)
    centros = pca.transform(km.cluster_centers_)
    plt.scatter(centros[:, 0], centros[:, 1], c="red", marker="X", s=200,
                edgecolor="black", label="Centroides")
    plt.title(f"K-Means (k={k_optimo}) proyectado con PCA "
              f"({pca.explained_variance_ratio_.sum()*100:.0f}% de varianza)")
    plt.xlabel("Componente 1"); plt.ylabel("Componente 2"); plt.legend()
    plt.savefig(f"{CARPETA}/grupos_pca.png", dpi=120, bbox_inches="tight"); plt.close()

    # 9) Dendrograma sobre el perfil promedio de cada estacion
    medias = df.groupby("estacion")[VARIABLES].mean()
    Z = linkage(StandardScaler().fit_transform(medias), method="ward")
    plt.figure(figsize=(10, 5))
    dendrogram(Z, labels=list(medias.index), leaf_rotation=60)
    plt.title("Dendrograma de estaciones (Ward)")
    plt.tight_layout()
    plt.savefig(f"{CARPETA}/dendrograma.png", dpi=120); plt.close()

    # 10) Guardar resultados
    df.to_csv(f"{CARPETA}/dataset_con_grupos.csv", index=False)
    with open(f"{CARPETA}/resultados_clustering.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(salida))
    print(f"\nArchivos guardados en '{CARPETA}/'")


if __name__ == "__main__":
    main()