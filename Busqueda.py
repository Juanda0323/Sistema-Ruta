# -*- coding: utf-8 -*-


import heapq
from Hechos import HECHOS, VELOCIDAD_COMERCIAL_KMH
from Motor import (
    construir_grafo,
    nodos_de_estacion,
    distancia_haversine_km,
)

# Índice rápido nombre -> hecho (para conocer lat/lon de una estación)
_HECHOS_POR_NOMBRE = {}
for h in HECHOS:
    _HECHOS_POR_NOMBRE.setdefault(h.nombre.strip().lower(), h)


def _nombre_de_nodo(nodo):
    return nodo.split("|")[0]


def heuristica(nodo, nombre_destino):
    """Estimación optimista (admisible) del tiempo restante hasta el
    destino: distancia en línea recta / velocidad comercial."""
    nombre_actual = _nombre_de_nodo(nodo)
    h_actual = _HECHOS_POR_NOMBRE.get(nombre_actual.strip().lower())
    h_destino = _HECHOS_POR_NOMBRE.get(nombre_destino.strip().lower())
    if h_actual is None or h_destino is None:
        return 0.0
    dist_km = distancia_haversine_km(h_actual.lat, h_actual.lon, h_destino.lat, h_destino.lon)
    return (dist_km / VELOCIDAD_COMERCIAL_KMH) * 60.0


def a_estrella(origen_nombre, destino_nombre, grafo=None, hechos=HECHOS):
    """
    Ejecuta A* entre dos nombres de estación.

    Retorna un diccionario con:
      - "encontrada": True/False
      - "ruta": lista de nodos ("Estacion|Linea") en orden, si se encontró
      - "tiempo_total_min": tiempo estimado total de viaje
      - "num_transbordos": cantidad de cambios de línea en la ruta
    """
    if grafo is None:
        grafo = construir_grafo(hechos)

    nodos_origen = nodos_de_estacion(origen_nombre, hechos)
    nodos_destino = set(nodos_de_estacion(destino_nombre, hechos))

    if not nodos_origen:
        return {"encontrada": False, "error": f"No existe la estación de origen '{origen_nombre}' en la base de conocimiento."}
    if not nodos_destino:
        return {"encontrada": False, "error": f"No existe la estación de destino '{destino_nombre}' en la base de conocimiento."}

    # costo_g: costo real acumulado desde el origen hasta cada nodo
    costo_g = {n: 0.0 for n in nodos_origen}
    padre = {n: None for n in nodos_origen}

    # Cola de prioridad: (f = g + h, contador_desempate, nodo)
    contador = 0
    abiertos = []
    for n in nodos_origen:
        f = costo_g[n] + heuristica(n, destino_nombre)
        heapq.heappush(abiertos, (f, contador, n))
        contador += 1

    visitados = set()

    while abiertos:
        f_actual, _, nodo_actual = heapq.heappop(abiertos)

        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        if nodo_actual in nodos_destino:
            return _reconstruir_resultado(nodo_actual, padre, costo_g)

        for arco in grafo.get(nodo_actual, []):
            vecino = arco.destino
            nuevo_costo = costo_g[nodo_actual] + arco.minutos
            if vecino not in costo_g or nuevo_costo < costo_g[vecino]:
                costo_g[vecino] = nuevo_costo
                padre[vecino] = nodo_actual
                f = nuevo_costo + heuristica(vecino, destino_nombre)
                heapq.heappush(abiertos, (f, contador, vecino))
                contador += 1

    return {"encontrada": False, "error": "No se encontró una ruta entre las estaciones indicadas."}


def _reconstruir_resultado(nodo_final, padre, costo_g):
    ruta = [nodo_final]
    while padre[ruta[-1]] is not None:
        ruta.append(padre[ruta[-1]])
    ruta.reverse()

    transbordos = 0
    for a, b in zip(ruta, ruta[1:]):
        if _nombre_de_nodo(a) == _nombre_de_nodo(b):
            transbordos += 1

    return {
        "encontrada": True,
        "ruta": ruta,
        "tiempo_total_min": costo_g[nodo_final],
        "num_transbordos": transbordos,
    }