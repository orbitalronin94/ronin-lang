# Guía de migración: Runtime v0.1 → v0.5

**Estado:** borrador preventivo para el candidato v0.5.0. No es una garantía de compatibilidad ni una instrucción para instalar una versión aún no publicada.

## Antes de migrar

- La versión Python publicada en los metadatos del repositorio sigue siendo `0.1.0`; el crate Rust también declara `0.1.0`.
- No instales ni fijes `ronin-lang==0.5.0` hasta que exista un tag y una GitHub Release oficiales.
- Consulta primero el [perfil candidato v0.5](runtime-v0.5-profile-proposal.md) y sus exclusiones. Runtime v0.5 y MDES v0.5 son versiones independientes.

## Proyectos `.ronin`

El candidato conserva el flujo declarativo del subconjunto documentado: `list`, `check`, `solve`, `run`, `compile`, `simulate` y `diagnose`. No se anuncia una nueva sintaxis general ni soporte para funciones, módulos/imports, macros, control de flujo o concurrencia.

Antes de actualizar:
1. Conserva una copia del proyecto y de los resultados usados como baseline.
2. Ejecuta `ronin check proyecto.ronin`.
3. Ejecuta `ronin solve proyecto.ronin` y compara fitness/asignaciones con tus resultados de referencia.
4. Si usas simulación, fija explícitamente la semilla y compara las trayectorias dentro de las tolerancias del perfil.
5. Si consumes CSV o IR, valida los nombres de columnas y el esquema JSON IR v1 en tu integración.

## Cambio importante al consumir resultados: deuda

El campo `debt` puede ser `null` (Python `None`) porque no existe un estimador normativo implementado. No lo conviertas automáticamente a `0`: ausencia de estimación no equivale a deuda cero.

Ejemplo de consumidor defensivo:

```python
debt = result.get("debt")
if debt is None:
    # No hay estimación disponible; no asumir cero.
    handle_unavailable_debt()
else:
    use_debt_estimate(debt)
```

Adapta los nombres `handle_unavailable_debt` y `use_debt_estimate` a tu aplicación.

## Diagnósticos y capacidades no incluidas

- `bootstrap_ci` permanece `null`; no hay intervalos bootstrap disponibles.
- La identificabilidad individual no debe inferirse solo a partir de un diagnóstico agregado.
- FIM/Jacobiano, SIR, D-óptimo y Sobol no son APIs estables del perfil v0.5 candidato.
- El límite CES cuando lambda tiende a cero y otros bloqueos OPEN-* no deben reinterpretarse fuera de las decisiones documentadas.

## CLI, CSV e IR

- La CLI común conserva los comandos y la selección documentados en el perfil.
- Python y Rust comparten resultados en el corpus probado, pero no se garantiza igualdad textual de errores ni igualdad de todos los códigos de salida.
- CSV exporta el esquema actual documentado en el quickstart.
- IR v1 es una salida normalizada; no existe importador IR→RONIN ni garantía de round-trip.

## Instalación cuando exista el release

Cuando la GitHub Release publique realmente 0.5.0, las instrucciones definitivas de instalación, hashes, plataformas y dependencias se añadirán aquí. No uses comandos de instalación de una versión futura antes de que el artefacto exista.

Para trabajar desde un checkout fuente durante el desarrollo:

```bash
python -m pip install -e .
pytest -q
cargo build --manifest-path rust/Cargo.toml --release --locked
```

## Alcance de compatibilidad

La guía final deberá enumerar:
- versión Python y plataformas efectivamente probadas;
- targets Rust y toolchain usados para los artefactos;
- cambios reales de API/CLI desde el último tag publicado;
- hashes de los artefactos;
- cualquier incompatibilidad descubierta durante el RC.

Hasta completar esa auditoría, esta guía es una lista de precauciones, no una promesa de compatibilidad.
