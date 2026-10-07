# -*- coding: utf-8 -*-
"""
generar_dataset.py - Fuente de datos para el modelo supervisado
================================================================

Construye el archivo dataset_viajes.csv reutilizando el sistema de la
actividad anterior:

  1) Para cada par de estaciones (origen, destino) se ejecuta A* y se
     extraen caracteristicas REALES de la ruta: distancia, numero de
     estaciones, numero de transbordos y tiempo base estimado.
  2) Para cada par se SIMULAN varios viajes en distintas condiciones de
     contexto (franja horaria, tipo de dia, lluvia) y se calcula un
     tiempo real de viaje con variacion aleatoria.
  3) Se etiqueta cada viaje segun cuanto se desvio del tiempo base:
        puntual / retraso_moderado / retraso_alto

IMPORTANTE (para la documentacion): las variables de contexto y el tiempo
real son SIMULADOS (no provienen de mediciones oficiales). Las
caracteristicas de la ruta si provienen del sistema de la actividad 2.

Uso:
    python generar_dataset.py
"""

import csv
import random
from Hechos import HECHOS
from Motor import construir_grafo, distancia_haversine_km
from Busqueda import a_estrella

SEMILLA = 42
VIAJES_POR_PAR = 8          # viajes simulados por cada par origen-destino
ARCHIVO_SALIDA = "dataset_viajes.csv"

FRANJAS = ["pico_manana", "valle", "pico_tarde", "noche"]
DIAS = ["habil", "fin_semana"]

# Factor multiplicativo que cada condicion aplica al tiempo base
FACTOR_FRANJA = {"pico_manana": 1.35, "valle": 1.00, "pico_tarde": 1.40, "noche": 0.95}
FACTOR_DIA = {"habil": 1.00, "fin_semana": 0.90}
FACTOR_LLUVIA = {0: 1.00, 1: 1.15}
EXTRA_POR_TRANSBORDO = 0.05  # cada transbordo aumenta la variabilidad


def etiquetar(razon):
    """Clasifica el viaje segun tiempo_real / tiempo_base."""
    if razon < 1.15:
        return "puntual"
    if razon < 1.40:
        return "retraso_moderado"
    return "retraso_alto"


def coordenadas(nombre):
    for h in HECHOS:
        if h.nombre == nombre:
            return h.lat, h.lon


def main():
    random.seed(SEMILLA)
    grafo = construir_grafo(HECHOS)
    estaciones = sorted(set(h.nombre for h in HECHOS))

    filas = []
    for origen in estaciones:
        for destino in estaciones:
            if origen == destino:
                continue
            res = a_estrella(origen, destino, grafo=grafo, hechos=HECHOS)
            if not res["encontrada"]:
                continue

            lat1, lon1 = coordenadas(origen)
            lat2, lon2 = coordenadas(destino)
            dist_km = distancia_haversine_km(lat1, lon1, lat2, lon2)
            n_est = len(res["ruta"])
            n_trans = res["num_transbordos"]
            t_base = res["tiempo_total_min"]

            for _ in range(VIAJES_POR_PAR):
                franja = random.choice(FRANJAS)
                dia = random.choice(DIAS)
                lluvia = random.choice([0, 0, 1])  # lluvia ~33% de los viajes

                factor = FACTOR_FRANJA[franja] * FACTOR_DIA[dia] * FACTOR_LLUVIA[lluvia]
                factor *= 1 + EXTRA_POR_TRANSBORDO * n_trans
                ruido = random.gauss(1.0, 0.08)
                t_real = t_base * factor * max(ruido, 0.7)

                filas.append({
                    "origen": origen,
                    "destino": destino,
                    "distancia_km": round(dist_km, 3),
                    "num_estaciones": n_est,
                    "num_transbordos": n_trans,
                    "tiempo_base_min": round(t_base, 2),
                    "franja_horaria": franja,
                    "tipo_dia": dia,
                    "lluvia": lluvia,
                    "tiempo_real_min": round(t_real, 2),
                    "nivel_retraso": etiquetar(t_real / t_base),
                })

    with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Dataset generado: {ARCHIVO_SALIDA}  ({len(filas)} registros)")


if __name__ == "__main__":
    main()