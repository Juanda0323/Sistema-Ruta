# -*- coding: utf-8 -*-
"""
motor_inferencia.py - Motor de reglas (Sistema Basado en Reglas)
=================================================================

Este módulo corresponde al capítulo 3 del libro de referencia (Sistemas
basados en reglas). Aquí se implementan las REGLAS LÓGICAS que, aplicadas
sobre los HECHOS de kb.py, permiten INFERIR el grafo de conexiones del
sistema de transporte (encadenamiento hacia adelante / forward chaining).

Regla 1 - Adyacencia dentro de una misma línea:
    SI  estacion(X, L, N,  ...)  Y  estacion(Y, L, N+1, ...)
    ENTONCES  conectado(X@L, Y@L, tiempo_tramo)   (bidireccional)

Regla 2 - Transbordo entre líneas:
    SI  estacion(X, L1, ...)  Y  estacion(X, L2, ...)  Y  L1 != L2
    ENTONCES  conectado(X@L1, X@L2, tiempo_transbordo)

Cada nodo del grafo resultante se identifica como "Nombre|Linea" porque una
misma estación física (mismo nombre) puede pertenecer a varias líneas.
"""

import math
from Hechos import HECHOS, VELOCIDAD_COMERCIAL_KMH, PENALIZACION_TRANSBORDO_MIN


def nodo_id(nombre, linea):
    """Identificador único de un nodo del grafo: estación + línea."""
    return f"{nombre}|{linea}"


def distancia_haversine_km(lat1, lon1, lat2, lon2):
    """Distancia en línea recta (km) entre dos coordenadas geográficas."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def tiempo_estimado_min(distancia_km, velocidad_kmh=VELOCIDAD_COMERCIAL_KMH):
    """Convierte una distancia en tiempo estimado de viaje (minutos)."""
    return (distancia_km / velocidad_kmh) * 60.0


class Arco:
    """Una arista del grafo (una conexión entre dos nodos)."""

    def __init__(self, origen, destino, minutos, tipo):
        self.origen = origen
        self.destino = destino
        self.minutos = minutos
        self.tipo = tipo  # "tramo" (misma línea) o "transbordo"

    def __repr__(self):
        return f"Arco({self.origen} -> {self.destino}, {self.minutos:.1f} min, {self.tipo})"


def regla_adyacencia_misma_linea(hechos):
    """
    Regla 1: dos estaciones consecutivas (mismo 'orden' +1) dentro de la
    MISMA línea quedan conectadas en ambos sentidos.
    """
    arcos = []
    por_linea = {}
    for h in hechos:
        por_linea.setdefault(h.linea, []).append(h)

    for linea, estaciones in por_linea.items():
        estaciones.sort(key=lambda h: h.orden)
        for a, b in zip(estaciones, estaciones[1:]):
            dist = distancia_haversine_km(a.lat, a.lon, b.lat, b.lon)
            minutos = tiempo_estimado_min(dist)
            n1, n2 = nodo_id(a.nombre, linea), nodo_id(b.nombre, linea)
            arcos.append(Arco(n1, n2, minutos, "tramo"))
            arcos.append(Arco(n2, n1, minutos, "tramo"))
    return arcos


def regla_transbordo_estaciones_compartidas(hechos):
    """
    Regla 2: si el mismo nombre de estación aparece en más de una línea,
    se infiere que allí es posible hacer TRANSBORDO, con una penalización
    de tiempo fija.
    """
    arcos = []
    por_nombre = {}
    for h in hechos:
        por_nombre.setdefault(h.nombre, []).append(h)

    for nombre, apariciones in por_nombre.items():
        lineas = sorted(set(h.linea for h in apariciones))
        if len(lineas) > 1:
            for i in range(len(lineas)):
                for j in range(len(lineas)):
                    if i != j:
                        n1 = nodo_id(nombre, lineas[i])
                        n2 = nodo_id(nombre, lineas[j])
                        arcos.append(Arco(n1, n2, PENALIZACION_TRANSBORDO_MIN, "transbordo"))
    return arcos


def construir_grafo(hechos=HECHOS):
    """
    Motor de inferencia por encadenamiento hacia adelante: aplica todas las
    reglas sobre los hechos y arma la base de conocimiento derivada (el
    grafo de conexiones), representada como lista de adyacencia.
    """
    arcos = []
    arcos += regla_adyacencia_misma_linea(hechos)
    arcos += regla_transbordo_estaciones_compartidas(hechos)

    grafo = {}
    for arco in arcos:
        grafo.setdefault(arco.origen, []).append(arco)
        grafo.setdefault(arco.destino, [])  # asegura que el nodo exista

    return grafo


def nodos_de_estacion(nombre_estacion, hechos=HECHOS):
    """Devuelve todos los nodos (uno por línea) que corresponden a un mismo
    nombre de estación física. Útil porque el usuario da el nombre de la
    estación sin especificar la línea."""
    nombre_norm = nombre_estacion.strip().lower()
    return [
        nodo_id(h.nombre, h.linea)
        for h in hechos
        if h.nombre.strip().lower() == nombre_norm
    ]