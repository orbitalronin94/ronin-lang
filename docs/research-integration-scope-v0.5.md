# Integración selectiva de investigación para Runtime v0.5

**Estado:** alcance técnico propuesto para el release; no modifica MDES ni aprueba semántica normativa.  
**Referencia de investigación:** [PR #35](https://github.com/orbitalronin94/ronin-lang/pull/35), rama `work/v1.0-diagnostic-foundation`.

## Decisión de alcance

Runtime v0.5 incorpora pruebas de robustez numérica y paridad reproducible que fortalecen el solver y el simulador existentes. No incorpora automáticamente todas las APIs de investigación de PR #35 al contrato estable.

La separación es deliberada: las herramientas que reciben Jacobianos, sensibilidades, observaciones, pesos, escalas o supuestos de ruido son diagnósticos de investigación. No son semántica del lenguaje ni sustituyen la evaluación normativa de MDES.

## Integración seleccionada

### 1. Paridad determinista del solver

Se incorpora `scripts/check_randomized_runtime_parity.py` desde PR #35, adaptado para invocar Python con el `coexistence_delta` explícito del proyecto, igual que el CLI Rust.

- 80 sistemas generados determinísticamente (16 por modelo): PUSFRE, CES, Hill, CES-Hill y full de orden 1.
- Semilla fija 1310.
- Comprueba fitness, asignación, conservación de recurso, coexistencia, degeneración, parámetros serializados y `k_min`.
- Incluye rechazo equivalente Python/Rust para un caso Hill degenerado con fitness total bajo flujo numérico.
- Tolerancias numéricas explícitas; no compara texto JSON completo.

### 2. Paridad determinista del simulador

Se incorpora `scripts/check_randomized_simulation_parity.py`, que reutiliza el generador anterior:

- 15 sistemas generados (3 por modelo).
- 24 pasos por sistema y semillas deterministas.
- Compara historial completo, estado final, eventos de extinción y supervivencia.
- Verifica finitud, no negatividad y pertenencia al símplex.
- Construye el binario Rust una vez para evitar recompilaciones por caso.

Ambos scripts se ejecutan en GitHub Actions como parte de los jobs de paridad del runtime. Su incorporación queda condicionada al CI del commit que los integra en esta rama.

## Mejoras numéricas ya presentes en el runtime base

La evaluación Hill en Python y Rust usa una forma logística en espacio logarítmico para evitar overflow en razones extremas `Omega/K`. Los tests unitarios existentes cubren ratios extremos. Esta mejora no necesita importarse de nuevo desde PR #35: ya está en la línea base.

## No incluido en el contrato estable v0.5

Las siguientes APIs nuevas de PR #35 se mantienen fuera del perfil estable de Runtime v0.5 y en revisión separada:

- Diagnóstico local desde Jacobianos/FIM y SVD.
- Diagnóstico temprano SIR con subregistro.
- Diseño de observaciones D-óptimo genérico y específico Hill.
- Índices Sobol de primer orden.
- Nuevos contratos de identificabilidad práctica/estructural.

Motivos:

1. Requieren entradas externas y supuestos explícitos sobre observaciones, pesos, escalas y ruido.
2. Son herramientas de investigación complementarias, no construcciones normativas de MDES v0.5.
3. Necesitan documentación API, límites matemáticos, pruebas negativas y revisión científica independiente antes de convertirse en compromiso de compatibilidad.
4. No deben alterar silenciosamente el resultado de `solve`, `run` o `diagnose` del runtime base.

El bootstrap continúa sin estimador en el runtime estable. No se genera ni se presenta ningún intervalo de confianza ficticio.

## Condiciones para una futura promoción

Cada API de investigación se incorporará en una PR independiente cuando tenga:

- contrato de entrada/salida y unidades documentadas;
- supuestos estadísticos y dominio de validez;
- tests analíticos y casos degenerados;
- paridad Python/Rust cuando ambos backends la soporten;
- distinción explícita entre identificabilidad local, práctica y estructural;
- aprobación de alcance antes de publicarse como API estable.

## Límite de la afirmación

La paridad aleatoria determinista amplía la cobertura de los modelos implementados; no demuestra conformidad integral con MDES v0.5, identificabilidad global ni validez empírica de parámetros.
