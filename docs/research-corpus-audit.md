# Auditoría de integración del corpus Papers para RONIN v1.0

**Estado:** revisión técnica de integración; no es aprobación de resultados científicos ni una norma semántica.
**Fecha de revisión:** 2026-11-02.
**Corpus:** [orbitalronin94/Papers](https://github.com/orbitalronin94/Papers).
**Objetivo:** separar resultados matemáticos transferibles, heurísticas dependientes del dominio y propuestas metodológicas que requieren validación independiente.

## 1. Regla de integración

Un resultado del corpus solo puede convertirse en comportamiento normativo de RONIN si se cumplen, como mínimo:

1. hipótesis, dominio y parametrización explícitos;
2. derivación reproducible y dimensionalmente coherente;
3. distinción entre resultado estructural/global, local y práctico;
4. contraejemplos y pruebas negativas;
5. implementación y fixtures reproducibles en Python y Rust cuando corresponda.

La existencia de código, una matriz de confusión sintética o un porcentaje alto de acierto no sustituye estos requisitos.

## 2. Hill: degeneración K–alpha_h

La aproximación sub-saturada

\[
H(\Omega;K,\alpha_h) \approx \Omega^{\alpha_h}K^{-\alpha_h}
\]

motiva la combinación \(A=K^{-\alpha_h}\). En el límite dominante, los datos pueden informar sobre A sin separar K y alpha_h. La integración ya recogida en `research-integration-identifiability.md` es compatible con esta lectura condicionada al régimen.

**No debe inferirse** que cualquier diseño con rango estrecho de Ω demuestra no-identificabilidad estructural del modelo Hill exacto. Tampoco que un rango amplio la garantice. La conclusión depende de las observaciones, el ruido, los parámetros de referencia, la parametrización y el criterio de rango.

**Punto de auditoría pendiente:** el corpus contiene afirmaciones no reconciliadas sobre el rango del Jacobiano y sobre si el invariante deja solo A o permite también identificar alpha_h bajo ciertas condiciones. La resolución debe basarse en el Jacobiano correcto de la función observada, no en el Jacobiano de una transformación de parámetros distinto.

**Decisión para v1.0:** mantener Hill local como diagnóstico de diseño, etiquetar sus umbrales como heurísticos calibrados y no emitir un certificado estructural global desde el rango de Ω.

## 3. PBPK: FIM, condición y calibración

La FIM construida desde sensibilidades es una herramienta local condicionada por el punto de referencia, diseño y modelo de error. El número de condición puede describir mala condición numérica/práctica, pero una FIM singular en un punto no prueba por sí sola no-identificabilidad estructural global; una FIM bien condicionada en un punto tampoco demuestra identificabilidad global.

Los umbrales de condición citados en el paper (incluidos 1e3 y 1e6) requieren conservar el procedimiento de calibración, el escalado y el dominio en que fueron validados. No deben convertirse en constantes universales del runtime.

**Decisión para v1.0:** exigir escalado paramétrico, tolerancia de rango declarada, valores singulares y supuestos del ruido en las APIs locales. Mantener separado el estado estructural del estado práctico.

## 4. Epidemiología con subreporte

La reducción de fase temprana

\[
C(t) \approx A e^{rt}, \qquad r=\beta-\gamma, \qquad A=\rho\beta I_0
\]

permite justificar que, en ese modelo reducido, se informen combinaciones observables en vez de estimaciones individuales no sustentadas. No autoriza extrapolar el resultado a toda la dinámica SIR no lineal, a cualquier ventana temporal ni a cualquier observación.

Un Jacobiano del campo vectorial respecto al estado no es intercambiable con el Jacobiano de las observaciones respecto a los parámetros. Para afirmaciones de identificabilidad paramétrica se necesita la matriz de sensibilidades correcta o una derivación equivalente.

**Punto de auditoría pendiente:** reconciliar la afirmación de persistencia de la degeneración rho–I0 con los escenarios de horizonte largo del propio artículo. Los resultados de fase temprana deben seguir delimitados a la aproximación reducida hasta que se resuelva esa discrepancia.

**Decisión para v1.0:** conservar el perfil temprano como diagnóstico local de una aproximación explícita; no presentarlo como resultado general del SIR.

## 5. Protocolo de 50 dominios

El protocolo combina FIM/SVD, un criterio de rango Ω, análisis simbólico, datasets embebidos y pruebas sintéticas. Es valioso como programa de experimentación, pero varias piezas miden objetos diferentes:

- Un determinante simbólico no nulo en un punto o diseño de dos observaciones puede respaldar rango local completo bajo las hipótesis usadas; no equivale automáticamente a una prueba global para todo el dominio.
- El número de condición de la FIM y el rango simbólico del Jacobiano no son el mismo criterio y no deben fusionarse en una sola etiqueta.
- Normalizar datasets Longley o Macrodata a [0,1] no los convierte por sí solo en observaciones válidas de una respuesta Hill ni justifica interpretar su rango como rango de exposición Ω.
- La clasificación por Ω (<1.5, 1.5–3, >=3 órdenes) necesita una población de referencia, diseño y protocolo de calibración independientes. No es un umbral universal de identificabilidad.
- Una accuracy del 100% sobre 50 dominios sintéticos generados bajo el mismo mecanismo que se evalúa no establece validez externa. Se requieren mecanismos alternativos, casos adversariales y validación fuera de muestra.
- Un test de asimetría de regresión no identifica causalidad de forma general sin sus hipótesis (por ejemplo, restricciones de ruido/no gaussianidad y ausencia de confusores relevantes).

**Decisión para v1.0:** no importar la clasificación de los 50 dominios como semántica del lenguaje. Tratarla como protocolo de investigación reproducible sujeto a auditoría de datos, hipótesis, falsos positivos y validación externa.

## 6. Perspective epistemológica

El propio artículo se identifica como Perspective y aclara que sus tesis fuertes son propuestas, no teoremas, y que los métodos FIM locales no sustituyen a herramientas estructurales globales. RONIN puede adoptar el principio operativo de diagnosticar antes de ajustar, siempre que el informe indique que el diagnóstico preliminar depende de valores típicos, diseño y supuestos.

El concepto de “parámetro fantasma” puede usarse como lenguaje explicativo, no como un nuevo estado matemático del solver sin definición formal.

## 7. Protocolo de testing 1310

El protocolo propone tests tipados, refutadores, severidad, integridad y auditoría asistida por IA. Puede inspirar una futura capa de QA y trazabilidad de RONIN, pero no debe mezclarse con la gramática ni con la semántica numérica del lenguaje.

Antes de adoptarlo como puerta de release habría que definir un perfil proporcional al riesgo, validar sus esquemas y herramientas, y separar controles obligatorios de recomendaciones. La presencia de nombres de modelos o versiones concretas en el documento no debe convertirse en dependencia de RONIN.

**Decisión para v1.0:** usar los principios verificables (caso de fallo explícito, determinismo donde proceda, trazabilidad, pruebas negativas y auditoría de resultados) sin declarar conformidad integral con el protocolo 1310.

## 8. Estado de integración

| Área | Uso admisible en v1.0 | Estado |
|---|---|---|
| Hill sub-saturado | Diagnóstico local condicionado, FIM estable y selección D-óptima de niveles Omega con advertencias | Parcial; derivación/rango pendiente de reconciliación; no es certificado estructural |
| PBPK/FIM | FIM/SVD genérica, diseño D-óptimo greedy y Sobol de primer orden sobre salidas suministradas | Parcial; modelo ODE PBPK, generación de muestras, segundo orden y calibración externa no incorporados |
| SIR temprano | Combinaciones r y A del modelo reducido | Parcial; no generalizar al SIR completo |
| 50 dominios | Corpus de pruebas de investigación, no semántica normativa | No integrado como conformidad |
| Epistemología | Principio de diagnóstico pre-ajuste con límites explícitos | Adoptado como orientación |
| Testing 1310 | Inspiración para trazabilidad y pruebas falsables | No adoptado como estándar de release |

## 9. Bloqueos que no se deben cerrar por inferencia

1. No aprobar ADR-0001 ni ADR-0002 mediante esta auditoría.
2. No elevar heurísticas de rango Ω a pruebas estructurales globales.
3. No usar Jacobianos del estado como sustitutos de sensibilidades paramétricas.
4. No afirmar validez externa a partir de datos sintéticos autorreferenciales.
5. No marcar como implementada una capacidad solo porque el paper incluya código.

Esta auditoría debe actualizarse cuando se aporten correcciones o nuevas versiones del corpus Papers.


## 10. Tratado del Método y CASCABEL

La revisión complementaria [research-treatise-cascabel-audit.md](research-treatise-cascabel-audit.md) amplía el alcance del corpus: identifica circularidad en el pre-registro sintético, ausencia de validación externa, fuga de información en la validación cruzada del anexo de comparación de modelos, métricas AIC/BIC no aplicables al modelo mínimo y una formulación del invariante Hill que no reduce la degeneración a A. También delimita CASCABEL como proyecto separado, no como capacidad del lenguaje RONIN.

Estas conclusiones se incorporan como brechas de investigación, no como cambios semánticos ni como aprobación de ADRs.
