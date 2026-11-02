# Auditoría complementaria: Tratado del Método y CASCABEL

**Estado:** revisión técnica de integración; no constituye aprobación de resultados ni una norma del lenguaje.
**Fecha:** 2026-11-02.
**Fuentes:** [Papers — Tratado del Periplo y del Método](https://github.com/orbitalronin94/Papers/blob/main/%23%20TRATADO%20DEL%20PERIPLO%20Y%20DEL%20M%C3%89TODO.md), [Papers — Hacia una lingüística computacional falsable](https://github.com/orbitalronin94/Papers/blob/main/%23%20Hacia%20una%20ling%C3%BC%C3%ADstica%20computacional%20falsable%3A%20veintiocho%20tesis%20operables%20en%20un%20generador%20de%20texto%20en%20espa%C3%B1ol.md).

Esta revisión complementa [research-corpus-audit.md](research-corpus-audit.md). No cambia la semántica de RONIN ni cierra ADRs.

## 1. Tratado del Periplo y del Método

El tratado aporta una formalización operativa útil como proceso de investigación: categorizar afirmaciones, diagnosticar antes de ajustar, examinar el espectro, declarar el régimen, buscar invariantes, delimitar el dominio y reportar errores. Es una guía metodológica, no una especificación ejecutable de RONIN.

### 1.1 Deuda 1: el pre-registro no valida todavía el criterio

El anexo declara 31 dominios pre-registrados, pero el propio archivo pre_registration.yaml etiqueta los casos como sintéticos. En debt_1_preregistration.py:

- generate_synthetic_domain genera respuestas Hill sintéticas con parámetros fijados a partir del rango de Ω.
- run_diagnostic ajusta una recta en log-log y usa la correlación de sus residuos con log(Ω) como detector de saturación.
- Si no detecta esa señal, asigna números de condición constantes (1e10, 1e4 o 1e2) según los mismos cortes de rango Ω que definen las clases.
- La etiqueta esperada del pre-registro también está asignada a partir de esos rangos.

Por tanto, la matriz de confusión mide principalmente consistencia de una regla construida con los mismos umbrales que generan las etiquetas. No es una estimación independiente de sensibilidad/especificidad frente a identificabilidad verdadera. El modo plumbing se reconoce correctamente como 100% por construcción. Los modos perturbados (heteroscedástico, contaminado y oscilante) prueban robustez frente a tres perturbaciones concretas, pero no reparan la circularidad de las etiquetas ni constituyen validación externa.

**Uso admisible:** test de ejecución del pipeline y exploración preliminar de sensibilidad a esas perturbaciones. No importar accuracy, umbrales ni etiquetas como garantías normativas del runtime.

### 1.2 Deuda 2: validación externa pendiente y predicciones no justificadas

debt_2_external_validation.py devuelve NO_DATA si no existe production_logs.csv. Además, las predicciones de referencia para tasa de contradicción y tiempo de recuperación se fijan en cero. Sin un modelo predictivo justificado, una definición operacional validada de los eventos y datos externos, el error calculado no valida capacidad predictiva del método.

**Uso admisible:** esqueleto de ingestión y reporte, no evidencia empírica. La deuda permanece abierta.

### 1.3 Deuda 3: comparación sintética con limitaciones de evaluación

generate_debt_3_data.py crea datasets sintéticos bajo cinco estructuras conocidas. Recuperar la estructura generadora puede ser un test de recuperación bajo ese diseño, pero no demuestra superioridad general de PUSFRE ni validez externa.

Se identifican además dos problemas metodológicos en debt_3_model_comparison.py:

1. La validación cruzada inicializa cada ajuste de fold con theta_opt, que se obtuvo ajustando previamente el modelo sobre el dataset completo. Esa inicialización incorpora información de los folds de prueba; por tanto, el cv_rmse no es una estimación limpia de generalización. Cada fold debe ajustar desde una inicialización independiente que no dependa del conjunto de prueba.
2. El modelo mínimo se añade con aic=0 y bic=0, aunque no tiene verosimilitud ni número de parámetros estimados. Excluirlo de la selección AIC/BIC evita que gane por ese cero, pero mostrar esos valores como si fueran comparables sigue siendo engañoso. Deben ser null/no aplicables o utilizarse un criterio definido para todos los modelos.

También debe comprobarse la convergencia y el éxito de los optimizadores antes de aceptar los valores de ajuste. El resultado descrito en el README debe entenderse como comparación sintética exploratoria, no como validación de la estructura universal del modelo.

### 1.4 Invariante Hill en el tratado

En §18 el tratado propone I(K, α)=(K^(−α), α). Esta pareja conserva dos grados de libertad y, para α>0, permite recuperar K a partir de ambos componentes; por sí sola no representa una reducción a la combinación identificable A=K^(−α) cuando los datos solo informan sobre A.

La formulación debe reconciliarse con la degeneración sub-saturada del paper Hill y con la discrepancia ya registrada para la Perspective epistemológica. No debe codificarse como invariante identificable sin especificar qué observables y qué equivalencia de parámetros se están considerando.

## 2. CASCABEL: documento técnico separado de RONIN

El preprint de lingüística describe MOTOR CASCABEL v0.1.0, un generador de texto en español con 28 tesis computables sobre estilo, autoría, entropía, corpus negativo y validación. Su dominio, objetos y contratos no son los del lenguaje de descripción de sistemas RONIN.

Algunas ideas —predicciones falsables, corpus negativo, pruebas de perturbación, invariancia bajo transformaciones y reporte de límites— pueden inspirar metodología de QA. Sin embargo:

- las tesis son hipótesis/operaciones del proyecto CASCABEL, no propiedades demostradas de RONIN;
- no se deben incorporar sus flags, métricas estilométricas, validadores o gramática a RONIN v1.0;
- afirmaciones como invariancia de entropía o firma estilométrica requieren validación independiente y no deben tratarse como invariantes universales;
- CASCABEL no constituye evidencia de conformidad del parser, solver, IR o runtime Python/Rust.

**Decisión para v1.0:** mantener CASCABEL fuera del perfil normativo. Si en el futuro se diseña una integración, deberá ser un paquete/interoperabilidad separado con contrato y pruebas propios.

## 3. Consecuencias para RONIN v1.0

| Elemento del corpus | Tratamiento |
|---|---|
| Siete fases del método | Orientación de investigación y trazabilidad; no semántica ejecutable |
| Pre-registro de 31 dominios | Test sintético/circular; no certificación de identificabilidad |
| Tres perturbaciones | Pruebas de robustez parciales; no validación externa |
| Deuda 2 | Pendiente por falta de datos externos y predicciones justificadas |
| Comparación de modelos | Exploración sintética; CV requiere corregir fuga de información |
| Invariante Hill del tratado | Abierto; reconciliar con la reducción a A |
| CASCABEL v0.1.0 | Proyecto separado; fuera del perfil RONIN v1.0 |

## 4. Acciones pendientes antes de reutilizar el anexo

1. Sustituir las etiquetas sintéticas derivadas del rango Ω por un ground truth independiente, definido analíticamente para modelos concretos y con alcance declarado.
2. Separar la regla que se evalúa del mecanismo que genera los datos y de la asignación de etiquetas.
3. Añadir casos adversariales cerca de los umbrales, errores de especificación, ruido y diseños donde el rango Ω no prediga por sí solo el rango de sensibilidades.
4. Corregir la validación cruzada para que ninguna decisión de ajuste o inicialización use datos del fold de prueba.
5. No reportar AIC/BIC para modelos sin likelihood definida; comprobar convergencia y restricciones de cada ajuste.
6. Mantener la validación externa como pendiente hasta disponer de datos con procedencia, esquema y métricas justificadas.

**Conclusión:** el tratado refuerza la disciplina de separar consistencia interna, robustez, validación externa y comparación de modelos. Precisamente por esa disciplina, sus resultados sintéticos no deben elevarse a garantías del lenguaje. Esta auditoría amplía el registro de investigación; no aprueba ADR-0001/0002 ni modifica el perfil candidato.
