
## 1. Fuente de datos

El proyecto de transporte masivo no dispone de registros reales de validaciones
de pasajeros, por lo que, como permite la guía, se **desarrolló un dataset con
una muestra de datos** mediante `Generar_DataSet_Estaciones.py`. Tiene dos orígenes:

| Origen | Variables | Naturaleza |
|---|---|---|
| Sistema de las actividades anteriores (`Hechos.py` y grafo de `Motor.py`) | `num_lineas`, `num_conexiones` | Calculadas de la estructura de la red (estaciones inspiradas en TransMilenio, datos educativos no oficiales) |
| Simulación de demanda | `pasajeros_*`, `pasajeros_total`, `proporcion_pico` | **Simuladas**: patrón de demanda según el tipo de estación más variación aleatoria (semilla 7, reproducible) |

> Limitación: la demanda es simulada, así que los grupos hallados reflejan los
> patrones definidos en la simulación y no la demanda real del sistema. Con
> validaciones reales de tarjeta, el mismo código serviría sin cambios.

## 2. Archivo `dataset_estaciones.csv`

Cada fila es **una estación durante un día hábil**. Hay 1080 registros
(18 estaciones × 60 días hábiles).

| Columna | Descripción |
|---|---|
| `estacion` | Nombre de la estación (identificación, no se usa para agrupar) |
| `dia` | Número de día hábil (1 a 60, identificación) |
| `num_lineas` | Líneas que pasan por la estación |
| `num_conexiones` | Estaciones vecinas directamente conectadas |
| `pasajeros_pico_manana` | Pasajeros en la franja pico de la mañana |
| `pasajeros_valle` | Pasajeros en la franja valle |
| `pasajeros_pico_tarde` | Pasajeros en la franja pico de la tarde |
| `pasajeros_noche` | Pasajeros en la franja noche |
| `pasajeros_total` | Suma de las cuatro franjas |
| `proporcion_pico` | (pico mañana + pico tarde) / total |
| `arquetipo_simulado` | Patrón con el que se generó la fila. **No se usa para agrupar**; solo valida los resultados al final |

## 3. Diferencia con el aprendizaje supervisado

No existe una columna objetivo. El algoritmo recibe solo las características de
cada estación-día y debe descubrir por sí mismo qué filas se parecen. Los grupos
no tienen nombre: se interpretan después observando su perfil promedio.

## 4. Preparación de los datos

- Se agrupa con 7 variables: las cuatro franjas de pasajeros, `num_lineas`,
  `num_conexiones` y `proporcion_pico`.
- **Estandarización** (media 0, desviación 1): K-Means usa distancias, y sin
  ella las variables con números grandes (pasajeros, miles) dominarían sobre
  las pequeñas (líneas, 1 o 2).
- Se excluyen `estacion`, `dia` y `arquetipo_simulado`.

## 5. Problema de aprendizaje no supervisado

Agrupamiento (*clustering*) con **K-Means** y **agrupamiento jerárquico
aglomerativo** (Palma Méndez, 2008, cap. 16): descubrir qué tipos de estación
existen según su perfil de demanda y conectividad.