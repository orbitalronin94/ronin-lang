# ADR-0001 — Límite CES cuando lambda tiende a cero

**Estado:** propuesta pendiente de aprobación normativa.  
**Ámbito:** semántica matemática, Python, Rust, fixtures y anexo normativo.

## Contexto

La documentación normativa actual contiene dos contratos incompatibles:

- La definición CES usa la media de potencia ponderada. Para pesos normalizados positivos, su límite cuando `lambda → 0` es la media geométrica ponderada.
- N.2 Test 3 afirma que `model = "ces"` con `lambda = 1e-7` debe recuperar PUSFRE.
- El apéndice CES-Saturada describe el límite geométrico.
- Los runtimes Python y Rust implementan el límite geométrico y existe un test que lo diferencia explícitamente de PUSFRE.

No es una diferencia de tolerancia numérica: son funciones distintas. En la forma actual, PUSFRE usa el producto de componentes con sus exponentes propios, mientras que el límite CES normalizado usa exponentes iguales a los pesos.

## Opciones consideradas

### A. Mantener el límite matemático CES y separar PUSFRE

- CES es la media de potencia ponderada.
- Con pesos normalizados, `lambda → 0` produce la media geométrica ponderada.
- PUSFRE sigue siendo un modelo distinto con su propia semántica.
- Se sustituye N.2 Test 3 por un vector normativo de media geométrica y se añade un test que demuestra que no debe confundirse con PUSFRE.

**Ventaja:** continuidad matemática de la familia CES y semántica explícita.  
**Coste:** cambia el contrato descrito en N.2 Test 3.

### B. Forzar que CES lambda=0 recupere PUSFRE

- Introduce un caso especial que no es el límite de la media CES normalizada actual.
- Puede producir una discontinuidad alrededor de cero o exigir redefinir pesos y exponentes.
- Mantiene el test normativo existente a costa de dejar de usar la semántica CES estándar en ese punto.

**Ventaja:** conserva el test heredado.  
**Coste:** requiere una nueva definición matemática; no puede presentarse como el límite CES sin demostrar equivalencia.

### C. Redefinir toda la familia CES para que su límite coincida con PUSFRE

- Cambia la normalización o la interpretación de pesos.
- Requiere rederivar la familia, revisar todos los modelos, defaults y vectores numéricos.
- No es un cambio local del solver.

**Ventaja:** podría unificar familias si existe una formulación coherente.  
**Coste:** es una revisión normativa amplia.

## Recomendación técnica pendiente de aprobación

La opción A parece la más coherente con la definición matemática de CES actualmente implementada, pero **no se adopta sin aprobación expresa del autor de MDES**:

1. Mantener la media geométrica ponderada como límite CES.
2. Mantener PUSFRE como modelo independiente.
3. No afirmar que `CES(lambda → 0) = PUSFRE` salvo que una redefinición formal futura lo demuestre.
4. Mantener pesos iguales `(1/3, 1/3, 1/3)` en el perfil implementado actual; los pesos configurables quedan fuera hasta que tengan sintaxis y validación normativas.
5. Sustituir N.2 Test 3 por un test con salida geométrica exacta y un test de no equivalencia con PUSFRE.

## Evidencia que debe acompañar la decisión

- Derivación del límite de CES para `lambda → 0`.
- Ejemplo numérico con componentes distintos de 1 para que la diferencia sea observable.
- Tests equivalentes en Python y Rust.
- Actualización coordinada de MDES, anexo normativo, apéndice CES, documentación y fixtures.
- Nota de compatibilidad para usuarios que asumían el Test 3 anterior.

## Estado de implementación

Los runtimes actuales siguen la opción A en el cálculo y en los tests de regresión. La norma documental todavía contradice ese comportamiento. Por tanto, no se declara cerrada la conformidad de CES hasta que esta ADR sea aprobada y todas las fuentes normativas se actualicen de forma coordinada.

## Consecuencia para v0.5

Si la ADR no se aprueba antes de congelar el perfil, CES con lambda próximo a cero debe quedar fuera del perfil estable o documentarse como comportamiento provisional. No se debe publicar una versión estable con norma, código y tests en desacuerdo.
