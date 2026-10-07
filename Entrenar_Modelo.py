
"""
entrenar_modelo.py - Aprendizaje supervisado con arbol de decision
===================================================================

Objetivo: predecir el NIVEL DE RETRASO de un viaje en el transporte masivo
(puntual / retraso_moderado / retraso_alto) a partir de las caracteristicas
de la ruta y del contexto del viaje.

Tecnica: arbol de decision (cap. 17 de Palma Mendez, 2008: aprendizaje de
arboles y reglas de decision). El arbol aprendido puede leerse como un
conjunto de reglas SI-ENTONCES, igual que las reglas de la actividad 2,
pero esta vez aprendidas automaticamente de los datos.

Uso:
    python entrenar_modelo.py
(requiere haber ejecutado antes: python generar_dataset.py)
"""

import os
import joblib
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # permite guardar graficos sin abrir ventanas
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)

ARCHIVO_DATOS = "dataset_viajes.csv"
CARPETA_RESULTADOS = "resultados"
SEMILLA = 42

# Variables de entrada (NO se incluye tiempo_real_min: seria "trampa", ya
# que la etiqueta se calcula a partir de el).
NUMERICAS = ["distancia_km", "num_estaciones", "num_transbordos",
             "tiempo_base_min", "lluvia"]
CATEGORICAS = ["franja_horaria", "tipo_dia"]
OBJETIVO = "nivel_retraso"


def main():
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

    # 1) Cargar datos
    df = pd.read_csv(ARCHIVO_DATOS)
    print(f"Registros cargados: {len(df)}")
    print("\nDistribucion de la variable objetivo:")
    print(df[OBJETIVO].value_counts())

    # 2) Preparar variables (codificacion one-hot de las categoricas)
    X = pd.get_dummies(df[NUMERICAS + CATEGORICAS], columns=CATEGORICAS)
    y = df[OBJETIVO]

    # 3) Separar entrenamiento (80%) y prueba (20%)
    X_ent, X_pru, y_ent, y_pru = train_test_split(
        X, y, test_size=0.2, random_state=SEMILLA, stratify=y)
    print(f"\nEntrenamiento: {len(X_ent)}  |  Prueba: {len(X_pru)}")

    # 4) Entrenar el arbol (profundidad limitada para evitar sobreajuste
    #    y mantener reglas legibles)
    modelo = DecisionTreeClassifier(max_depth=4, min_samples_leaf=20,
                                    random_state=SEMILLA)
    modelo.fit(X_ent, y_ent)

    # 5) Evaluar
    pred = modelo.predict(X_pru)
    exactitud = accuracy_score(y_pru, pred)
    cv = cross_val_score(modelo, X, y, cv=5)
    informe = classification_report(y_pru, pred)

    print(f"\nExactitud en prueba: {exactitud:.3f}")
    print(f"Validacion cruzada (5 pliegues): {cv.mean():.3f} +/- {cv.std():.3f}")
    print("\nInforme de clasificacion:\n", informe)

    # 6) Reglas aprendidas (interpretabilidad)
    reglas = export_text(modelo, feature_names=list(X.columns))
    print("Reglas aprendidas por el arbol:\n", reglas)

    importancias = pd.Series(modelo.feature_importances_, index=X.columns)
    importancias = importancias.sort_values(ascending=False)
    print("Importancia de las variables:\n", importancias.round(3))

    # 7) Guardar resultados
    with open(f"{CARPETA_RESULTADOS}/resultados.txt", "w", encoding="utf-8") as f:
        f.write(f"Registros: {len(df)}\n")
        f.write(f"Exactitud en prueba: {exactitud:.3f}\n")
        f.write(f"Validacion cruzada (5 pliegues): {cv.mean():.3f} +/- {cv.std():.3f}\n\n")
        f.write("Informe de clasificacion:\n" + informe + "\n")
        f.write("Reglas aprendidas:\n" + reglas + "\n")
        f.write("Importancia de variables:\n" + importancias.round(3).to_string() + "\n")

    plt.figure(figsize=(20, 9))
    plot_tree(modelo, feature_names=list(X.columns),
              class_names=list(modelo.classes_), filled=True, fontsize=8)
    plt.savefig(f"{CARPETA_RESULTADOS}/arbol_decision.png", dpi=120,
                bbox_inches="tight")
    plt.close()

    ConfusionMatrixDisplay(confusion_matrix(y_pru, pred, labels=modelo.classes_),
                           display_labels=modelo.classes_).plot(cmap="Blues")
    plt.savefig(f"{CARPETA_RESULTADOS}/matriz_confusion.png", dpi=120,
                bbox_inches="tight")
    plt.close()

    joblib.dump((modelo, list(X.columns)), f"{CARPETA_RESULTADOS}/modelo.joblib")
    print(f"\nArchivos guardados en la carpeta '{CARPETA_RESULTADOS}/'")


if __name__ == "__main__":
    main()