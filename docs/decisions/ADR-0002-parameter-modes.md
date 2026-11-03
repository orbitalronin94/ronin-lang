# ADR-0002 — Declaración explícita de parámetros libres y fijados

**Estado:** propuesta de diseño pendiente de aprobación.  
**Ámbito:** parser, modelo, validación, IR, diagnóstico Python/Rust.

## Problema

El diagnóstico actual infiere:

- `K_free = K != inf`;
- `alpha_h_free = alpha_h != 1.0`.

El valor numérico no indica si el usuario ha fijado un parámetro o si desea estimarlo. En particular, `alpha_h = 1.0` puede ser un valor explícitamente fijado o simplemente el default. De forma análoga, un K finito puede ser un valor conocido fijado por el usuario o un parámetro que desea estimar.

La distinción afecta a `degeneracy`, `K_identifiable` y `alpha_h_identifiable`. Inferir libertad a partir del valor introduce una afirmación no contenida en el programa.

## Opciones

### A. Mantener inferencia por valor

No requiere cambios de sintaxis, pero conserva la ambigüedad y puede producir informes falsos. No recomendable para un perfil estable.

### B. Lista explícita de parámetros libres

Ejemplo:

```ronin
params: {
  model: "ces_hill",
  lambda: 0.5,
  K: 0.5,
  alpha_h: 1.0,
  free_parameters: ["K", "alpha_h"]
}
```

Los parámetros no incluidos se consideran fijados. La lista debe validarse contra el modelo y los parámetros existentes.

**Ventaja:** sintaxis compacta y fácil de inspeccionar.  
**Coste:** no permite declarar explícitamente “desconocido” y puede inducir a interpretar la ausencia como fijación deliberada.

### C. Mapa explícito de modos

Ejemplo:

```ronin
params: {
  model: "ces_hill",
  lambda: 0.5,
  K: 0.5,
  alpha_h: 1.0,
  parameter_modes: {
    K: "free",
    alpha_h: "fixed"
  }
}
```

Modos propuestos: `free`, `fixed`, `unknown`. La ausencia de modo equivale a `unknown`, no a una inferencia por valor.

**Ventaja:** representa fielmente el estado epistémico y evita suposiciones silenciosas.  
**Coste:** más sintaxis, validación y campos IR.

## Recomendación técnica pendiente de aprobación

La opción C parece representar mejor la diferencia entre valor numérico y conocimiento del usuario, pero **no se adopta sin aprobación expresa**:

1. El estado libre/fijado/desconocido debe ser explícito y ortogonal al valor numérico.
2. Los defaults no deben contar como una declaración de fijación ni de libertad.
3. Si el modo es `unknown`, el diagnóstico no debe afirmar identificabilidad individual condicionada a libertad; debe devolver `unknown` o un estado separado de “no evaluable”.
4. Los runtimes no deben inferir `free` a partir de `K < inf` ni de `alpha_h != 1`.
5. El modo se conserva en AST/modelo e IR y se valida contra el modelo seleccionado.
6. La paridad Python/Rust debe cubrir parámetros libres, fijados y desconocidos, incluidos valores iguales a defaults.

## Compatibilidad y migración

- Los proyectos existentes sin `parameter_modes` se parsean y resuelven igual que antes.
- Sus campos de identificabilidad pasan a `unknown` cuando dependan de una libertad no declarada; no se reinterpretan silenciosamente.
- Se puede ofrecer un modo transitorio `legacy` solo si se documenta como heurística y no como contrato estable.
- No se cambia la fórmula del solver: este campo gobierna diagnóstico e inferencia, no el valor de fitness.

## Tests de aceptación

- `alpha_h: 1.0` con modo `free` y `fixed` produce diagnósticos distintos.
- `K: 0.5` con modo `free` y `fixed` produce diagnósticos distintos.
- Modo omitido produce `unknown`, sin inferir desde el valor.
- Parámetros no admitidos por el modelo se rechazan.
- Python y Rust conservan modos idénticos en JSON IR.
- El solver numérico es idéntico independientemente de los modos, salvo en los campos de diagnóstico.

## Estado

La implementación actual todavía usa la heurística histórica por valor. Esta ADR propone reemplazarla antes de congelar un perfil estable; no debe considerarse aprobada hasta que el autor confirme la semántica y se actualicen MDES, parser, IR, runtimes, fixtures y documentación.

## Consecuencia para v0.5

Hasta que exista decisión aprobada e implementación, la identificabilidad individual que dependa de inferir libertad a partir de valores permanece provisional o fuera del perfil estable. No se cambia la fórmula del solver por esta ADR.
