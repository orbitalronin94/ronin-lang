# Primer flujo práctico: repartir un recurso con RONIN

Este recorrido usa el fixture versionado `examples/maquinas.ronin`. Su objetivo es enseñar el flujo que está implementado hoy en el runtime, no la sintaxis de una futura capa de scripting.

## El problema

Dos máquinas compiten por 100 horas de trabajo:

| Máquina | Capacidad (`phi`) | Consistencia (`psi`) | Frecuencia inicial |
|---|---:|---:|---:|
| A | 0.8 | 1.0 | 0.6 |
| B | 0.5 | 1.0 | 0.4 |

La pregunta es cómo reparte el modelo PUSFRE el recurso a partir de esos parámetros.

## 1. Instalar y comprobar el entorno

Desde la raíz del repositorio:

```bash
python -m pip install -e .
ronin --version
pytest -q
```

La instalación editable registra el comando `ronin`. La suite completa sirve como comprobación del checkout; no es necesario ejecutarla para cada uso cotidiano.

## 2. Inspeccionar y validar el proyecto

```bash
ronin list examples/maquinas.ronin
ronin check examples/maquinas.ronin
```

El primer comando enumera los sistemas declarados. El segundo valida todos los sistemas del archivo y debe responder:

```text
OK (1 systems)
```

Si la validación falla, no continúes interpretando una resolución: corrige primero el archivo y vuelve a ejecutar `check`.

## 3. Resolver el sistema

```bash
ronin solve examples/maquinas.ronin
```

La solución de referencia del fixture es:

- Fitness: `[0.48, 0.20]`
- Asignación: aproximadamente `[70.5882352941, 29.4117647059]`

Las asignaciones suman el recurso disponible (100). En este ejemplo, la máquina A recibe aproximadamente 70.59 horas y la B 29.41 horas.

El resultado JSON también incluye información del modelo utilizado, umbral de coexistencia, diagnóstico y advertencias. No interpretes `debt: null` como deuda cero: significa que el estimador de deuda todavía no está implementado.

## 4. Ejecutar todos los sistemas y exportar

Para obtener resultados JSON de todos los sistemas del archivo:

```bash
ronin run examples/maquinas.ronin
```

Para generar CSV:

```bash
ronin run examples/maquinas.ronin --format csv
```

El CSV contiene las columnas `system`, `agent_index`, `model`, `fitness` y `allocation`. Puedes redirigirlo a un archivo:

```bash
ronin run examples/maquinas.ronin --format csv > maquinas.csv
```

## 5. Guardar una representación intermedia

```bash
ronin compile examples/maquinas.ronin -o maquinas.ir.json
```

Esto valida el proyecto y escribe el JSON IR normalizado. El IR permite inspeccionar o integrar la representación del proyecto sin tener que volver a interpretar manualmente el texto fuente.

## 6. Simular con semilla fija

```bash
ronin simulate examples/maquinas.ronin --steps 100 --seed 42
```

La semilla fija hace reproducible la trayectoria para el mismo runtime y contrato de simulación. No significa que el modelo sea una predicción empírica ni que una semilla concreta sea representativa de todos los escenarios.

## 7. Diagnosticar

```bash
ronin diagnose examples/maquinas.ronin
```

El diagnóstico informa, entre otras cosas, del rango de frecuencias y del estado de degeneración de los parámetros Hill. Para este fixture, las frecuencias 0.6 y 0.4 cubren un rango estrecho; no hay base para afirmar que los parámetros de saturación se puedan identificar a partir de esos datos.

## 8. Segundo escenario: cinco flotas

El repositorio incluye `examples/pesca.ronin`, un escenario de cinco agentes con un recurso total de 10.000 unidades. Los parámetros son datos de ejemplo del fixture; no son una serie observacional ni una estimación empírica de flotas reales.

Ejecuta:

```bash
ronin list examples/pesca.ronin
ronin check examples/pesca.ronin
ronin solve examples/pesca.ronin
ronin run examples/pesca.ronin --format csv > pesca.csv
ronin diagnose examples/pesca.ronin
```

Este segundo caso sirve para practicar la misma cadena de trabajo con más partes y comparar cómo cambia la asignación al cambiar capacidad, consistencia, frecuencia y el parámetro de competencia. Conserva los dos archivos originales y modifica copias si quieres experimentar; así podrás reproducir el caso base.

## Qué demuestra y qué no demuestra este ejemplo

**Sí demuestra:** que el runtime actual puede leer un proyecto RONIN, validarlo, resolver su asignación, emitir resultados estructurados, exportar CSV/IR y ejecutar una simulación reproducible.

**No demuestra:** que el reparto sea óptimo para cualquier sistema real, que los parámetros sean estimaciones empíricas, ni que estén implementadas todas las capacidades de MDES v0.5. El fixture es un caso de aceptación sintético y pequeño.

## Ejecutar el mismo caso en Rust

Desde el directorio `rust/`:

```bash
cargo run -- check ../examples/maquinas.ronin
cargo run -- solve ../examples/maquinas.ronin
cargo run -- run ../examples/maquinas.ronin --format csv
cargo run -- compile ../examples/maquinas.ronin -o ../maquinas.ir.json
```

La paridad Python/Rust está verificada para un subconjunto compartido mediante las suites del repositorio. No debe interpretarse como paridad completa de todas las características de MDES.

## Siguientes pasos

- Cambia `resource` o los valores de los agentes y vuelve a ejecutar `check` y `solve`.
- Compara escenarios guardándolos como archivos separados.
- Prueba otros fixtures ejecutables del directorio `examples/`.
- Consulta [cobertura y límites](source-coverage.md) antes de depender de una característica avanzada.
