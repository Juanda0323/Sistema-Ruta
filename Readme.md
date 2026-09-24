# Sistema Inteligente de Ruteo en Transporte Masivo

Sistema desarrollado en Python que, a partir de una **base de conocimiento
escrita en reglas lógicas**, determina la **mejor ruta** entre un punto A y
un punto B en un sistema de transporte masivo, usando **búsqueda
heurística (A\*)**.

## Estructura del proyecto y su relación con la teoría

| Archivo               | Contenido                                              | Tema del libro guía          |
|-----------------------|---------------------------------------------------------|-------------------------------|
| `kb.py`                | Hechos: estaciones, líneas, orden, coordenadas          | Cap. 2 - Lógica y representación del conocimiento |
| `motor_inferencia.py`  | Reglas lógicas (adyacencia y transbordo) + motor forward-chaining que construye el grafo | Cap. 3 - Sistemas basados en reglas |
| `busqueda.py`          | Algoritmo A\* con heurística de distancia Haversine     | Cap. 9 - Técnicas basadas en búsquedas heurísticas |
| `main.py`              | Interfaz de línea de comandos (integra todo lo anterior)| —                              |

## Requisitos

- Python 3.8 o superior (no requiere librerías externas, solo librería estándar).

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
# 1) Ver todas las estaciones disponibles en la base de conocimiento
python main.py --listar

# 2) Modo directo: indicar origen (A) y destino (B)
python main.py "Portal Norte" "Portal Americas"

# 3) Modo interactivo (te pregunta origen y destino)
python main.py
```

### Ejemplo de salida

```
=== MEJOR RUTA ENCONTRADA ===
  Tramo 1 - Linea L1:
      Portal Norte  ->  Toberin  ->  Calle 146  ->  Calle 100  ->  Calle 85  ->  Heroes  ->  Calle 72  ->  Av Jimenez
      >> TRANSBORDO <<
  Tramo 2 - Linea L3:
      Av Jimenez  ->  Tercer Milenio  ->  Restrepo  ->  Banderas  ->  Portal Americas

Tiempo total estimado : 81.9 minutos
Numero de transbordos : 1
Numero de estaciones  : 13
```

## Cómo adaptarlo a otra ciudad / otro sistema real

Todo el conocimiento del dominio vive en **`kb.py`**. Para usar tu propio
sistema de transporte (otra ciudad, otro conjunto de líneas), solo debes:

1. Editar la lista `HECHOS` con tus propias estaciones: nombre, línea a la
   que pertenece, orden dentro de la línea y coordenadas (lat, lon).
2. Repetir el mismo `nombre` de estación en más de una línea para que el
   sistema infiera automáticamente que allí existe un transbordo.
3. (Opcional) Ajustar `VELOCIDAD_COMERCIAL_KMH` y
   `PENALIZACION_TRANSBORDO_MIN` a valores reales de tu sistema.

No es necesario tocar `motor_inferencia.py`, `busqueda.py` ni `main.py`:
las reglas y el algoritmo de búsqueda son independientes de los datos.

## Cómo funciona internamente (resumen para el video/PDF)

1. **Hechos** (`kb.py`): cada estación se declara como un hecho
   `(nombre, línea, orden, lat, lon)`.
2. **Reglas lógicas** (`motor_inferencia.py`):
   - *Regla de adyacencia*: si dos estaciones son consecutivas
     (`orden`, `orden+1`) dentro de la misma línea, quedan conectadas en
     ambos sentidos, con un costo en minutos calculado a partir de la
     distancia real entre sus coordenadas.
   - *Regla de transbordo*: si el mismo nombre de estación aparece en más
     de una línea, se infiere una conexión especial de "transbordo" con una
     penalización fija de tiempo.
   - El **motor de inferencia** aplica ambas reglas sobre todos los hechos
     (encadenamiento hacia adelante) y arma el grafo completo del sistema.
3. **Búsqueda heurística A\*** (`busqueda.py`): explora el grafo priorizando
   los caminos con menor `f(n) = g(n) + h(n)`, donde `g(n)` es el tiempo
   real acumulado y `h(n)` es una estimación optimista (distancia en línea
   recta hasta el destino) que nunca sobreestima el costo real, garantizando
   que la ruta encontrada es la óptima.
4. **`main.py`** integra todo: construye el grafo a partir de los hechos y
   las reglas, ejecuta A\* entre el punto A y el punto B indicados por el
   usuario, y muestra la ruta resultante con sus tramos, transbordos y
   tiempo total estimado.

## Pendientes de la actividad que este código NO cubre

Este proyecto resuelve el **punto 3** de la guía (el sistema en Python).
Recuerda que la actividad también pide:

- Punto 4: grabar un video corto (máx. 10 min) explicando el proyecto, los
  comandos ejecutados y los resultados obtenidos, con la participación de
  todo el equipo.
- Punto 5 / Entregable: subir el código a un repositorio Git/GitLab
  (agregando al tutor como colaborador), y entregar un PDF con el enlace al
  repositorio y las pruebas realizadas.