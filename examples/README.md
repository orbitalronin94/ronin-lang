# Ejemplos RONIN 1.1

La colección del documento maestro adjunto no contiene 130 bloques completos:

- Los ejemplos **1–100** se describen como material conservado de una versión anterior, pero sus cuerpos no aparecen en el Markdown entregado. No se han inventado ni reconstruido.
- Los ejemplos **101–119** conservan sus declaraciones `system` cuando incluyen agentes literales. Los comandos posteriores (`solve`, `simulate`, `diagnose`, bucles) quedan fuera del subconjunto que acepta el parser Python actual.
- El ejemplo **115** usa `generate_users(10)`; se conserva como plantilla parser-only porque el generador no está implementado.
- Los ejemplos **120–130** incluyen marcadores de posición, generadores o datos omitidos. Los ficheros identifican expresamente los esqueletos parser-only y no fabrican datasets.
- El ejemplo 130 usa tres sistemas con composición de parámetros avanzada; se representan como tres declaraciones mínimas para probar el parser.

## Verificación

`tests/test_examples.py` comprueba que todos los ficheros `.ronin` se parsean y contienen al menos una declaración de sistema. Esto **no** significa que todos sean ejecutables ni que superen la validación semántica: las plantillas con agentes vacíos son deliberadamente parser-only.

## Ejemplos base

Maquinas, Pesca, CES y degeneración siguen siendo los fixtures ejecutables y validados por el runtime.

---

# RONIN 1.1 examples (English)

The supplied master document does not include 130 complete examples. Examples 1–100 are referenced as material retained from an earlier edition, but their bodies are absent from the supplied file. Examples 101–130 include literal system declarations, placeholders, generators or omitted datasets. The repository preserves available declarations and marks parser-only scaffolds explicitly; it does not invent missing records.

The example test checks parsing only, not semantic validity or end-to-end execution. The validated runtime fixtures remain Maquinas, Pesca, CES and the degeneracy examples.
