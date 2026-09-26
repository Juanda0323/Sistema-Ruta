# -*- coding: utf-8 -*-


from collections import namedtuple

HechoEstacion = namedtuple("HechoEstacion", ["nombre", "linea", "orden", "lat", "lon"])

# Velocidad comercial promedio asumida para el sistema (km/h).
# Se usa para transformar distancia -> tiempo estimado (minutos).
VELOCIDAD_COMERCIAL_KMH = 25.0

# Penalización de tiempo (minutos) que representa el hecho de bajarse de un
# bus/tren y caminar/esperar para tomar otra línea en una estación de
# transbordo.
PENALIZACION_TRANSBORDO_MIN = 5.0

# ---------------------------------------------------------------------------
# HECHOS: estaciones por línea (orden ascendente = sentido de recorrido)
# ---------------------------------------------------------------------------
HECHOS = [
    # Línea 1 (L1) - Troncal Autonorte / Caracas (sentido norte -> centro)
    HechoEstacion("Portal Norte",  "L1", 1, 4.7519, -74.0453),
    HechoEstacion("Toberin",       "L1", 2, 4.7376, -74.0448),
    HechoEstacion("Calle 146",     "L1", 3, 4.7280, -74.0421),
    HechoEstacion("Calle 100",     "L1", 4, 4.6883, -74.0491),
    HechoEstacion("Calle 85",      "L1", 5, 4.6689, -74.0562),
    HechoEstacion("Heroes",        "L1", 6, 4.6584, -74.0693),
    HechoEstacion("Calle 72",      "L1", 7, 4.6538, -74.0637),
    HechoEstacion("Av Jimenez",    "L1", 8, 4.6017, -74.0721),

    # Línea 2 (L2) - Troncal NQS (sentido norte -> sur)
    HechoEstacion("Portal 80",       "L2", 1, 4.7132, -74.1109),
    HechoEstacion("Polo",            "L2", 2, 4.6789, -74.0776),
    HechoEstacion("NQS Calle 30",    "L2", 3, 4.6317, -74.0904),
    HechoEstacion("Ricaurte",        "L2", 4, 4.6183, -74.0918),
    HechoEstacion("Tercer Milenio",  "L2", 5, 4.5944, -74.0910),
    HechoEstacion("Restrepo",        "L2", 6, 4.5766, -74.1055),
    HechoEstacion("Molinos",         "L2", 7, 4.5674, -74.1024),
    HechoEstacion("Portal Sur",      "L2", 8, 4.5052, -74.1259),

    # Línea 3 (L3) - Eje centro -> occidente (comparte estaciones de
    # transbordo con L1 y L2: Av Jimenez, Tercer Milenio, Restrepo)
    HechoEstacion("Av Jimenez",     "L3", 1, 4.6017, -74.0721),
    HechoEstacion("Tercer Milenio", "L3", 2, 4.5944, -74.0910),
    HechoEstacion("Restrepo",       "L3", 3, 4.5766, -74.1055),
    HechoEstacion("Banderas",       "L3", 4, 4.6291, -74.1330),
    HechoEstacion("Portal Americas","L3", 5, 4.6259, -74.1568),

    # Línea 4 (L4) - Alimentador corto que conecta L1 con L2
    HechoEstacion("Calle 85", "L4", 1, 4.6689, -74.0562),
    HechoEstacion("Polo",     "L4", 2, 4.6789, -74.0776),
]