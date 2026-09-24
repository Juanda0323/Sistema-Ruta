# -*- coding: utf-8 -*-
"""
main.py - Sistema Inteligente de Ruteo en Transporte Masivo
=============================================================

Punto de entrada del sistema. Integra:
  1) kb.py               -> base de conocimiento (hechos)
  2) motor_inferencia.py  -> reglas lógicas (construcción del grafo)
  3) busqueda.py          -> búsqueda heurística A* (mejor ruta)

MODO DE USO
-----------
1) Modo interactivo (te pregunta la estación de origen y destino):
       python main.py

2) Modo por argumentos (útil para el video/demo, o para probar varias
   rutas rápidamente):
       python main.py "Portal Norte" "Portal Americas"

3) Listar todas las estaciones disponibles en la base de conocimiento:
       python main.py --listar
"""

import sys
from Hechos import HECHOS


def listar_estaciones():
    nombres = sorted(set(h.nombre for h in HECHOS))
    print("\nEstaciones disponibles en la base de conocimiento:")
    for n in nombres:
        lineas = sorted(set(h.linea for h in HECHOS if h.nombre == n))
        print(f"  - {n}  (linea(s): {', '.join(lineas)})")
    print()


def formatear_ruta(resultado):
    ruta = resultado["ruta"]
    lineas_texto = []
    linea_actual = None
    tramo_estaciones = []

    def cerrar_tramo():
        if tramo_estaciones:
            lineas_texto.append((linea_actual, tramo_estaciones[:]))

    for nodo in ruta:
        nombre, linea = nodo.split("|")
        if linea != linea_actual:
            cerrar_tramo()
            tramo_estaciones = [nombre]
            linea_actual = linea
        else:
            tramo_estaciones.append(nombre)
    cerrar_tramo()

    print("\n=== MEJOR RUTA ENCONTRADA ===")
    for i, (linea, estaciones) in enumerate(lineas_texto, start=1):
        print(f"  Tramo {i} - Linea {linea}:")
        print(f"      {'  ->  '.join(estaciones)}")
        if i < len(lineas_texto):
            print("      >> TRANSBORDO <<")

    print(f"\nTiempo total estimado : {resultado['tiempo_total_min']:.1f} minutos")
    print(f"Numero de transbordos : {resultado['num_transbordos']}")
    print(f"Numero de estaciones  : {len(ruta)}")
    print("=" * 32 + "\n")


def ejecutar(origen, destino):
    from busqueda import a_estrella  # import local para no romper --listar

    print(f"\nBuscando la mejor ruta entre '{origen}' y '{destino}' ...")
    grafo = construir_grafo(HECHOS)
    resultado = a_estrella(origen, destino, grafo=grafo, hechos=HECHOS)

    if not resultado["encontrada"]:
        print(f"\n[ERROR] {resultado['error']}\n")
        print("Usa 'python main.py --listar' para ver las estaciones disponibles.\n")
        return

    formatear_ruta(resultado)


def main():
    args = sys.argv[1:]

    if args and args[0] in ("--listar", "-l"):
        listar_estaciones()
        return

    if len(args) >= 2:
        origen, destino = args[0], args[1]
    else:
        listar_estaciones()
        origen = input("Estacion de origen (punto A): ").strip()
        destino = input("Estacion de destino (punto B): ").strip()

    ejecutar(origen, destino)


if __name__ == "__main__":
    main()