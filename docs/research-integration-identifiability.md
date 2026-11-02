# Integración del corpus de identificabilidad en RONIN

**Estado:** propuesta de ingeniería para v1.0; no es todavía una norma aprobada.  
**Ámbito:** diagnóstico K–α, diagnósticos locales por FIM/SVD y contrato de reporte.

Este documento integra críticamente el corpus de investigación de [Papers](https://github.com/orbitalronin94/Papers). Los trabajos técnicos del corpus son autopublicados y no revisados por pares; la Perspective declara expresamente que sus propuestas conceptuales no son teoremas. Por tanto, RONIN adopta aquí requisitos de trazabilidad y reproducibilidad, no convierte automáticamente cada umbral o afirmación empírica del corpus en una garantía matemática.

## 1. Principio de diseño

El diagnóstico de identificabilidad debe estar disponible **antes del ajuste principal** y también después del ajuste. Es un análisis preliminar condicionado por el modelo, los datos, el ruido supuesto y los valores típicos de parámetros. No es un oráculo independiente de los datos ni sustituye los métodos globales de identificabilidad estructural.

RONIN distinguirá:

1. **Identificabilidad estructural:** propiedad del modelo y del mapa parámetros→observables. Cuando se necesita una afirmación global, usar análisis simbólico/global o una prueba analítica; una FIM local no basta.
2. **Identificabilidad local:** rango del Jacobiano de observables respecto a parámetros en un punto de referencia. La FIM local puede ayudar bajo hipótesis de regularidad.
3. **Identificabilidad práctica:** condicionamiento de la información disponible para un diseño, ruido y rango de datos concretos.
4. **Estimabilidad:** comportamiento de un procedimiento estimador concreto bajo el muestreo y el modelo de error especificados. No se deduce solo de la FIM.

La frontera entre lo estructural y lo práctico puede ser difusa en modelos singulares o casi degenerados. El informe debe preservar esa incertidumbre.

## 2. Contrato matemático local

Para observaciones \(y_i = f(x_i;\theta) + \varepsilon_i\), el Jacobiano local es:

\[
J_{ij}=\frac{\partial f(x_i;\theta)}{\partial\theta_j}
\]

Con matriz de pesos de observación \(W\), la información local es:

\[
\mathcal I(\theta)=J^T W J
\]

RONIN debe calcular el rango y los valores singulares de un Jacobiano **escalado**. El escalado es obligatorio para que el diagnóstico no dependa arbitrariamente de las unidades de los parámetros. Cuando sea posible, se analizarán parámetros transformados (por ejemplo, log-parametrización para parámetros estrictamente positivos).

Requisitos del informe:

- valores típicos de parámetros y parametrización usados;
- diseño/observaciones, modelo de error y pesos;
- rango numérico, tolerancia usada y valores singulares;
- número de condición, o infinito si la matriz es singular;
- direcciones débiles del espacio paramétrico;
- sensibilidad del resultado a valores típicos y escalado;
- limitaciones de la aproximación local y de la hipótesis de regularidad.

La SVD identifica direcciones locales débiles. Los parámetros con mayor peso en un vector singular son una heurística de atribución, no una caracterización completa de una variedad de degeneración. RONIN no debe inventar un invariante a partir de esa lista: los invariantes requieren derivación analítica, reparametrización identificable o validación adicional.

## 3. Instancia Hill: degeneración K–αh

Para:

\[
H(\Omega;K,\alpha_h)=
\frac{\Omega^{\alpha_h}}{K^{\alpha_h}+\Omega^{\alpha_h}}
\]

en el régimen sub-saturado \(\Omega/K\) pequeño, la aproximación dominante es:

\[
H(\Omega;K,\alpha_h)\approx
\Omega^{\alpha_h}K^{-\alpha_h}
\]

y, en escala logarítmica:

\[
\log H \approx
\alpha_h\log\Omega-\alpha_h\log K
\]

Esto motiva reportar la combinación \(A=K^{-\alpha_h}\) cuando los datos no separan K y \(\alpha_h\). No implica que cualquier rango estrecho haga estructuralmente no identificable al modelo Hill exacto para todo conjunto finito de parámetros: la clasificación operativa depende del régimen, ruido, diseño y parametrización.

El umbral de tres órdenes de magnitud es una heurística calibrada para condiciones concretas en el paper Hill del corpus. El propio corpus posterior advierte que depende de \(\alpha_h\), ruido y parametrización. Por ello:

- no se usará como teorema ni como umbral universal;
- no se inferirá identificabilidad solo a partir de max(Ω)/min(Ω);
- se reportará también la posición de Ω respecto a K (saturación/sub-saturación);
- los umbrales de 1.5 y 3 órdenes solo podrán activarse en un perfil Hill explícito y se marcarán como heurísticos calibrados;
- un resultado local FIM/SVD y un resultado analítico/global se presentarán por separado.

## 4. Qué puede diagnosticar el runtime actual

El modelo System contiene Φ, Ψ, frecuencias y parámetros, pero no contiene una serie de observaciones \(y_i\), un diseño experimental ni un modelo de error. Por tanto, diagnose(system) **no puede calcular una FIM empírica ni certificar identificabilidad práctica**.

El informe actual basado en el rango de frecuencias es un diagnóstico estructural/heurístico de diseño, no una evaluación de información observacional. Debe etiquetarse así hasta que exista una API que reciba observaciones y supuestos de ruido explícitos.

No es válido construir una FIM tratando el fitness predicho por el mismo conjunto de parámetros como si fueran observaciones independientes: eso sería circular.

## 5. API de diagnóstico de diseño Hill

La API Python incluye el diagnóstico de diseño Hill en `ronin.identifiability.diagnose_hill_design`, el motor genérico `diagnose_jacobian` y el perfil epidemiológico `diagnose_sir_early_phase`. Recibe el diseño Ω, valores típicos K y αh, y σ bajo un modelo de error gaussiano aditivo homoscedástico. Calcula la FIM local en coordenadas `log(K), log(alpha_h)`, sus valores singulares, rango numérico, número de condición y dirección débil. También informa el rango Ω, la fracción de puntos por encima de un umbral configurable Ω/K y los supuestos usados.

Esta primera entrega **no recibe respuestas observadas ni realiza ajuste**: es un diagnóstico pre-ajuste del diseño. No declara identificabilidad estructural, práctica ni estimabilidad; esos estados permanecen explícitamente como `not_assessed` o `not_calibrated`. Los módulos Rust equivalentes están implementados. Los scripts `scripts/check_hill_design_parity.py` y `scripts/check_sir_diagnostic_parity.py` comparan ambos runtimes en CI. Todavía falta integrar el diagnóstico en la CLI/IR y validar umbrales prácticos por dominio.

La API ampliada para futuras respuestas observadas y diagnósticos post-ajuste debe aceptar explícitamente:

- observaciones predictoras Ω;
- respuestas observadas y;
- modelo de respuesta (Hill en el primer perfil);
- valores típicos de K y \(\alpha_h\);
- modelo/escala de ruido y su magnitud;
- límites y transformaciones de parámetros;
- tolerancias numéricas y número mínimo de observaciones.

La API debe rechazar datos no finitos, dimensiones incompatibles, observaciones fuera del dominio declarado y configuraciones de ruido inválidas. No ajustará parámetros ni ejecutará bootstrap de forma implícita.

El resultado mínimo debe separar:

- structural_status (solo cuando exista prueba global/analítica);
- local_rank_status;
- practical_status;
- estimability_status (desconocido hasta evaluar un estimador);
- omega_range_orders;
- saturation_fraction respecto a K;
- fim_condition_number;
- singular_values;
- weak_parameter_directions;
- typical_parameters;
- assumptions;
- warnings y recommendation.

Cuando un campo no pueda calcularse, será null/unknown, nunca una afirmación implícita de identificabilidad.


### Perfil SIR con subreporte

El corpus incluye además el paper de epidemiología con la aproximación de fase temprana:

En la aproximación reducida: `C(t) ≈ A * exp(r*t)`, con `r = beta - gamma` y `A = rho * beta * I0`.

La API `diagnose_sir_early_phase` calcula el Jacobiano local de `log C(t)` respecto a las coordenadas logarítmicas de `beta, gamma, rho, I0`. En ese modelo reducido, el rango es como máximo 2 para cuatro parámetros: se reportan las combinaciones `growth_rate` y `observed_amplitude`, no estimaciones individuales ficticias. El estado se limita expresamente a la aproximación de fase temprana; no se extrapola a todo el SIR no lineal.

El motor genérico `diagnose_jacobian` acepta un Jacobiano evaluado en parámetros típicos, pesos de observación y escalas paramétricas. Calcula FIM/SVD local para otros dominios sin fingir que dispone de un modelo dinámico o de datos que el llamador no ha proporcionado.

La construcción numérica de la FIM normaliza primero el Jacobiano ponderado y escalado antes de formar (J^T W J). Esto evita que el simple cambio de unidades común provoque overflow/underflow al elevar entradas al cuadrado. Las pruebas cubren escalas comunes (10^{-200}) y (10^{200}), verificando que rango y condición se conservan y que los valores singulares recuperan la escala física. La diagonalización Jacobi usa además un criterio de parada relativo a la magnitud de la matriz, no un umbral absoluto ligado a la unidad.

## Ejemplos de uso de las APIs locales

Los ejemplos siguientes son diagnósticos de diseño; no realizan ajuste de parámetros ni demuestran identificabilidad global.

### Diseño Hill

```python
from ronin import diagnose_hill_design

report = diagnose_hill_design(
    omega=[0.01, 0.1, 1.0, 10.0, 100.0],
    K=1.0,
    alpha_h=1.5,
    sigma=0.05,
)
print(report.local_rank_status)
print(report.fim_condition_number)
print(report.warnings)
```

El ruido `sigma` se interpreta como desviación típica de errores gaussianos aditivos independientes sobre la respuesta Hill. Los valores `K` y `alpha_h` son parámetros típicos en los que se linealiza el diseño.

### Jacobiano de un modelo propio

```python
from ronin import diagnose_jacobian

report = diagnose_jacobian(
    jacobian=[
        [1.0, 2.0],
        [2.0, 4.0],
        [3.0, 6.0],
    ],
    weights=[1.0, 1.0, 1.0],
    parameter_names=("K", "alpha_h"),
    parameter_scales=(1.0, 1.0),
)
print(report.local_rank_status)  # rank_deficient
print(report.weak_directions)
```

El llamador es responsable de proporcionar el Jacobiano en los valores típicos y con la parametrización documentada. `weights` contiene precisiones diagonales de observación; `parameter_scales` define las escalas de coordenadas paramétricas. El resultado es local.

### SIR temprano con subreporte

```python
from ronin import diagnose_sir_early_phase

report = diagnose_sir_early_phase(
    times=range(31),
    beta=0.4,
    gamma=0.15,
    rho=0.1,
    I0=100.0,
    sigma=0.1,
)
print(report.growth_rate)       # beta - gamma
print(report.observed_amplitude)  # rho * beta * I0
print(report.local_information.local_rank)  # como máximo 2
```

Aquí `sigma` es la desviación típica de errores gaussianos independientes sobre `log(C(t))). La conclusión se limita a la aproximación de fase temprana descrita en el paper; no debe aplicarse al SIR no lineal completo.

## 6. Protocolo operativo

1. Validar modelo, observaciones, parámetros típicos y modelo de ruido.
2. Comprobar si hay una degeneración estructural conocida o una reparametrización identificable demostrada.
3. Calcular el diagnóstico local escalado (Jacobian/SVD/FIM) bajo las hipótesis declaradas.
4. Repetirlo en una colección de valores típicos plausibles y reportar sensibilidad.
5. Si el modelo es localmente mal condicionado, identificar direcciones débiles y buscar invariantes; no ajustar/reportar individualmente parámetros débiles como si los datos los determinasen.
6. Solo después ejecutar el ajuste principal, perfiles de verosimilitud o bootstrap, según el modelo de error.
7. Reportar por separado predicción, parámetros, priors/constraints e invariantes.

## 7. Reglas de implementación v1.0

- Ningún umbral empírico se eleva a norma universal sin calibración y evidencia reproducible.
- No se confunde FIM singular con prueba global de no-identificabilidad sin hipótesis de regularidad.
- El diagnóstico siempre registra los valores típicos usados y su sensibilidad.
- Se distingue parámetro fijado por el usuario de parámetro libre; el valor por defecto no demuestra que el usuario lo haya fijado.
- Python y Rust comparten fixtures de datos, resultados esperados, tolerancias y estados.
- Si no hay datos observacionales suficientes, se informa unknown y se explica qué falta.
- Bootstrap, ajuste y perfiles de verosimilitud son etapas posteriores, no sustitutos de la clasificación estructural.
- La CLI/API rechaza `bootstrap > 0` hasta que exista un estimador implementado; `bootstrap=0` solo solicita el diagnóstico disponible. El campo `bootstrap_ci` permanece `null` y no se ignora silenciosamente una petición de bootstrap.

## 8. Fuentes del corpus

- [Epistemología de la Degeneración: Cuándo un Parámetro No Es una Medición](https://github.com/orbitalronin94/Papers) — Perspective; diagnóstico pre-ajuste, límites de FIM local, dependencia de valores típicos y distinción entre degeneración estructural/práctica.
- [No-Identificabilidad de los Parámetros de la Ecuación de Hill en el Régimen Sub-Saturado](https://github.com/orbitalronin94/Papers) — análisis K–\(\alpha_h\), umbrales Hill y código de referencia.
- [No-Identificabilidad Estructural y Práctica en Modelos PBPK](https://github.com/orbitalronin94/Papers) — FIM/SVD, condicionamiento y calibración dependiente del dominio.

Estos documentos son fuentes de investigación del proyecto, no sustitutos de una revisión independiente de las derivaciones, datos y código reproducible.


## 9. Integración crítica del resto del corpus Papers

El repositorio Papers contiene documentos adicionales a los tres artículos de identificabilidad inicialmente revisados. Su estado de integración en RONIN es:

- **No-identificabilidad epidemiológica con subreporte:** el perfil SIR de fase temprana se implementa en Python y Rust. La afirmación se limita a la aproximación reducida C(t) ≈ A * exp(r*t), con r = beta - gamma y A = rho * beta * I0; no se generaliza al SIR completo ni a fases con saturación.
- **Protocolo de validación de 50 dominios:** no se toma el 100% sintético como validación externa. Las clases esperadas se construyen con el mismo criterio de rango Ω que se evalúa; eso mide consistencia del clasificador con su pre-registro, no generalización independiente. El propio documento reporta un falso positivo en saturación (ΔBIC = −18.04) y reconoce que el determinante estático no sustituye STRIKE-GOLDD completo para EDOs.
- **Protocolo de testing 1310:** se adopta como dirección metodológica (refutador explícito, condición de fallo, integridad/versionado y segregación entre propuesta, ejecución y auditoría). No se incorporan como dependencias obligatorias Pydantic, LLMs, ML ni estándares regulatorios ajenos al runtime. La validación semántica automatizada de refutadores sigue siendo trabajo futuro.
- **Epistemología Generativa:** la separación entre capa exploratoria y formal, la categorización A/B/C/D y la estructura E/O/F/P/R pueden gobernar la trazabilidad de hipótesis y pruebas. No convierten una proposición en demostrada por el mero hecho de estar pre-registrada.
- **Tratado del Periplo y del Método:** se adoptan sus cuatro principios de trabajo —diagnosticar antes de ajustar, categorizar antes de afirmar, delimitar antes de generalizar y pre-registrar antes de testear— como criterios de ingeniería y revisión.
- **Lingüística computacional / Motor Cascabel:** es un proyecto y dominio independiente. Sus 28 tesis operables no se incorporan como requisitos del lenguaje RONIN; su protocolo de falsabilidad puede servir como patrón de diseño de tests.

La página README de Papers declara cuatro documentos, pero el árbol actual del repositorio contiene más archivos. La integración se basa en los documentos realmente presentes, no en el inventario resumido del README.


## 10. Auditoría matemática crítica del paper Hill

La integración del paper Hill se limita deliberadamente a diagnóstico local de diseño y no adopta su afirmación de no-identificabilidad estructural como regla automática. Hay una inconsistencia algebraica que debe corregirse antes de elevar el Teorema 4.1 a contrato del runtime.

El paper define `A = K^(-n_H)` y después afirma que la transformación `(K, n_H) -> (A, n_H)` tiene Jacobiano de rango 1. Para `K > 0` y `n_H > 0`, el Jacobiano correcto es:

```text
J = [[-n_H * K^(-n_H-1), -A * ln(K)],
     [0,                    1       ]]

det(J) = -n_H * K^(-n_H-1) != 0
```

Por tanto, la transformación tiene rango 2 y es invertible; de hecho, `K = A^(-1/n_H)`. Si los datos identifican de forma independiente `A` y `n_H`, también determinan `K`. No se puede concluir simultáneamente que ambos `A, n_H` son identificables y que el par `K, n_H` no lo es a partir de esa transformación.

Además, el texto alterna entre “solo A es identificable” y “reportar A y n_H”, que son afirmaciones diferentes. Deben reconciliarse.

La Perspective *Epistemología de la Degeneración* §3.3 define el invariante como una función que separa fibras distintas, y en §5.1 escribe `I(K,n_H) = (K^(-n_H), n_H)`. Ese par también determina `K` de forma única, por lo que sus fibras son puntos, no la curva `K^(-n_H)=A0` de §3.1. Si el invariante pretendido es únicamente `A`, entonces la curva sí existe, pero `n_H` no puede presentarse a la vez como una segunda cantidad identificada por ese mismo mapa. Esta contradicción entre el paper Hill y la Perspective debe resolverse explícitamente.

Esto no niega la **no-identificabilidad práctica** en diseños sub-saturados: cuando la respuesta es pequeña, el ruido, el rango de Ω, el número de puntos y la replicación pueden hacer que la FIM esté mal condicionada y que la incertidumbre de `K` sea enorme. Tampoco niega que, en un límite asintótico estricto, desaparezcan términos de orden superior. Pero el umbral operativo `Omega/K < 0.1` no demuestra por sí solo una pérdida de rango estructural para cualquier diseño con múltiples valores Ω.

Decisión de ingeniería actual:

- `diagnose_hill_design` informa FIM/SVD local, rango numérico, condicionamiento y advertencias.
- `structural_status` permanece `not_assessed`; no se cambia a “non-identifiable” usando solo el umbral 0.1.
- No se implementa una salida normativa de “solo A” hasta que el paper distinga formalmente el modelo exacto, el modelo asintótico, la identificabilidad estructural y la práctica.
- La revisión debe incluir derivación corregida, dominio de validez, diseño mínimo de observaciones y tests que puedan refutar la clasificación.

Este bloqueo ejemplifica la regla del Tratado: categorizar y delimitar antes de afirmar.


## 11. Auditoría metodológica crítica del paper PBPK

El paper PBPK define correctamente la identificabilidad estructural mediante inyectividad del mapa parámetros → salida, pero después afirma como Propiedad 3.2 que una FIM singular implica no-identificabilidad estructural. Esa implicación no se sigue de la definición anterior.

Una FIM singular calculada sobre un conjunto finito de tiempos, una parametrización y un punto nominal demuestra que el diseño/sensibilidad local no aporta rango completo en esas condiciones. Puede ser evidencia de no-identificabilidad local o práctica, pero no prueba por sí sola que el mapa completo de salidas sea globalmente no inyectivo. La conclusión estructural requiere una simetría/invariante analítica, un argumento de observabilidad/identificabilidad para el sistema dinámico o una herramienta global apropiada. En sentido inverso, rango local completo tampoco garantiza inyectividad global.

También deben quedar explícitas dos dependencias:

- El número de condición de la FIM depende de la escala y parametrización de los parámetros. Los umbrales 1e3 y 1e6 no son universales sin definir coordenadas adimensionales, escalado, modelo de ruido, diseño y tolerancia numérica.
- Los índices de Sobol miden influencia sobre la varianza de una salida bajo distribuciones/rangos elegidos. Un índice bajo no demuestra identificabilidad ni justifica automáticamente fijar un parámetro; parámetros correlacionados pueden ser influyentes y aun así estar confundidos.

La degeneración específica Vt–Kp del modelo PBPK mínimo sí puede formularse mediante la reparametrización del estado tisular: al definir `z = Ct/Kp`, la dinámica de `z` depende de `Vt*Kp`. Si la única salida observada es Cp y no hay otras ecuaciones/observaciones que separen ambos parámetros, la simetría del producto ofrece un argumento estructural concreto. Esa demostración específica no valida la regla general “FIM singular ⇒ estructuralmente no identificable”.

Decisión de ingeniería:

- La FIM/SVD genérica de RONIN informa rango y condicionamiento **locales**, nunca un veredicto estructural global por sí sola.
- Las afirmaciones estructurales requieren una invariante/simetría demostrada y un dominio de validez explícito.
- Los umbrales se guardan como calibraciones de un perfil/dominio, no como constantes universales del lenguaje.
- Los índices de sensibilidad global se reportan como influencia bajo las distribuciones declaradas, separados de identificabilidad.



## 12. Auditoría de consistencia del paper SIR con subreporte

La implementación RONIN se limita a la aproximación explícita de fase temprana, donde la observación se reduce a dos combinaciones:

- `r = beta - gamma`;
- `A = rho * beta * I0`.

En ese modelo reducido, cuatro parámetros individuales no pueden recuperarse a partir de dos combinaciones; la conclusión está delimitada y la API reporta las combinaciones.

El paper completo necesita reconciliar dos afirmaciones distintas:

1. La Proposición 4.2 afirma que la degeneración `rho-I0` persiste incluso con ventanas largas.
2. La Tabla 7.2 presenta el escenario S8 (300 días, rango amplio) con condición 45.21 y ningún parámetro problemático, es decir, una clasificación identificable.

También se usa el rango del Jacobiano del sistema dinámico respecto a los estados en el equilibrio libre de enfermedad como confirmación de degeneración paramétrica. Ese Jacobiano de estado `df/dy` no es el Jacobiano de sensibilidades de la salida respecto a parámetros `dC/dtheta`; su rango, por sí solo, no demuestra identificabilidad o no-identificabilidad de parámetros.

Para resolverlo se debe especificar con precisión:
- qué parámetros iniciales se conocen y cuáles se estiman;
- si `S0` se fija como `N-I0` o como dato independiente;
- qué observaciones se usan (casos incidentes, prevalencia, serología, recuperados);
- qué modelo de ruido y ventana temporal se asumen;
- si la conclusión aplica al SIR completo o solo a la aproximación temprana;
- qué Jacobiano/FIM se calcula para la inferencia de parámetros.

Decisión de ingeniería: la API actual no extrapola el resultado temprano al SIR completo y no adopta la afirmación de persistencia `rho-I0` como regla universal hasta que el paper reconcilie Proposición 4.2, S8 y el Jacobiano pertinente.


### Estados explícitos en el informe RONIN

El informe `diagnose` expone ahora por separado:

- `structural_status = "not_assessed"`;
- `practical_status = "not_calibrated"`;
- `estimability_status = "not_assessed"`;
- `diagnostic_method = "omega_range_heuristic"`;
- `parameter_freedom_basis = "legacy_value_heuristic"`.

Estos campos hacen visible el alcance real del informe y la heurística histórica de libertad paramétrica. No convierten el diagnóstico por rango Ω en una prueba FIM ni en un análisis global. La migración a modos explícitos `free/fixed/unknown` está propuesta en ADR-0002.
