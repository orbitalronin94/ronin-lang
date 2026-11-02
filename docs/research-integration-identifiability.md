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

La primera API Python ya está implementada en `ronin.identifiability.diagnose_hill_design`. Recibe el diseño Ω, valores típicos K y αh, y σ bajo un modelo de error gaussiano aditivo homoscedástico. Calcula la FIM local en coordenadas `log(K), log(alpha_h)`, sus valores singulares, rango numérico, número de condición y dirección débil. También informa el rango Ω, la fracción de puntos por encima de un umbral configurable Ω/K y los supuestos usados.

Esta primera entrega **no recibe respuestas observadas ni realiza ajuste**: es un diagnóstico pre-ajuste del diseño. No declara identificabilidad estructural, práctica ni estimabilidad; esos estados permanecen explícitamente como `not_assessed` o `not_calibrated`. Todavía falta implementar el mismo contrato en Rust, añadir integración CLI/IR y validar umbrales prácticos por dominio.

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

## 8. Fuentes del corpus

- [Epistemología de la Degeneración: Cuándo un Parámetro No Es una Medición](https://github.com/orbitalronin94/Papers) — Perspective; diagnóstico pre-ajuste, límites de FIM local, dependencia de valores típicos y distinción entre degeneración estructural/práctica.
- [No-Identificabilidad de los Parámetros de la Ecuación de Hill en el Régimen Sub-Saturado](https://github.com/orbitalronin94/Papers) — análisis K–\(\alpha_h\), umbrales Hill y código de referencia.
- [No-Identificabilidad Estructural y Práctica en Modelos PBPK](https://github.com/orbitalronin94/Papers) — FIM/SVD, condicionamiento y calibración dependiente del dominio.

Estos documentos son fuentes de investigación del proyecto, no sustitutos de una revisión independiente de las derivaciones, datos y código reproducible.
