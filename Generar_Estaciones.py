
"""
Generar_DataSet_Estaciones.py - Fuente de datos para aprendizaje NO supervisado
================================================================================

Construye dataset_estaciones.csv: la demanda diaria de pasajeros de cada
estacion del sistema de transporte, dividida por franja horaria.

Origen de los datos:
  - REALES (del sistema de las actividades anteriores): num_lineas y
    num_conexiones de cada estacion, calculados a partir de Hechos.py y del
    grafo de Motor.py.
  - SIMULADOS: los pasajeros por franja horaria de cada dia habil. No hay
    datos reales de validaciones, asi que se generan con un patron de
    demanda segun el tipo de estacion, mas variacion aleatoria.

La columna 'arquetipo_simulado' guarda con que patron se genero cada fila.
NO se usa para agrupar (el clustering no conoce etiquetas); solo sirve
despues para verificar si los grupos encontrados coinciden con la
estructura oculta.

Uso:
    python Generar_DataSet_Estaciones.py
"""

import csv
import random
from Hechos import HECHOS
from Motor import construir_grafo

SEMILLA = 7
DIAS_HABILES = 60
ARCHIVO_SALIDA = "dataset_estaciones.csv"

FRANJAS = ["pico_manana", "valle", "pico_tarde", "noche"]

# Volumen diario base de pasajeros y reparto por franja (suma = 1) segun el
# tipo de estacion.
PATRON = {
    "terminal":   {"volumen": 14000, "reparto": [0.40, 0.20, 0.30, 0.10]},
    "transbordo": {"volumen": 20000, "reparto": [0.30, 0.30, 0.30, 0.10]},
    "intermedia": {"volumen": 6000,  "reparto": [0.28, 0.25, 0.32, 0.15]},
}


def clasificar_estaciones():
    """Deriva, a partir de los hechos y el grafo, las caracteristicas
    estructurales de cada estacion."""
    grafo = construir_grafo(HECHOS)
    max_orden = {}
    for h in HECHOS:
        max_orden[h.linea] = max(max_orden.get(h.linea, 0), h.orden)

    info = {}
    for nombre in sorted(set(h.nombre for h in HECHOS)):
        apariciones = [h for h in HECHOS if h.nombre == nombre]
        lineas = set(h.linea for h in apariciones)
        es_extremo = any(h.orden == 1 or h.orden == max_orden[h.linea]
                         for h in apariciones)

        vecinos = set()
        for h in apariciones:
            for arco in grafo.get(f"{h.nombre}|{h.linea}", []):
                if arco.tipo == "tramo":
                    vecinos.add(arco.destino.split("|")[0])

        if len(lineas) >= 2:
            arquetipo = "transbordo"
        elif es_extremo:
            arquetipo = "terminal"
        else:
            arquetipo = "intermedia"

        info[nombre] = {
            "num_lineas": len(lineas),
            "num_conexiones": len(vecinos),
            "arquetipo": arquetipo,
        }
    return info


def main():
    random.seed(SEMILLA)
    info = clasificar_estaciones()

    # Cada estacion tiene su propia "personalidad" fija: un factor de
    # volumen y un pequeno sesgo en el reparto por franjas.
    personalidad = {}
    for nombre, datos in info.items():
        base = PATRON[datos["arquetipo"]]
        reparto = [r * random.uniform(0.85, 1.15) for r in base["reparto"]]
        total = sum(reparto)
        personalidad[nombre] = {
            "factor": random.uniform(0.8, 1.2),
            "reparto": [r / total for r in reparto],
        }

    filas = []
    for nombre, datos in info.items():
        base = PATRON[datos["arquetipo"]]
        pers = personalidad[nombre]
        for dia in range(1, DIAS_HABILES + 1):
            total_dia = base["volumen"] * pers["factor"] * random.gauss(1.0, 0.10)
            pasajeros = [max(0, int(total_dia * r * random.gauss(1.0, 0.10)))
                         for r in pers["reparto"]]
            total = sum(pasajeros)
            filas.append({
                "estacion": nombre,
                "dia": dia,
                "num_lineas": datos["num_lineas"],
                "num_conexiones": datos["num_conexiones"],
                "pasajeros_pico_manana": pasajeros[0],
                "pasajeros_valle": pasajeros[1],
                "pasajeros_pico_tarde": pasajeros[2],
                "pasajeros_noche": pasajeros[3],
                "pasajeros_total": total,
                "proporcion_pico": round((pasajeros[0] + pasajeros[2]) / total, 4),
                "arquetipo_simulado": datos["arquetipo"],
            })

    with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)

    print(f"Dataset generado: {ARCHIVO_SALIDA}  ({len(filas)} registros, "
          f"{len(info)} estaciones x {DIAS_HABILES} dias habiles)")


if __name__ == "__main__":
    main()