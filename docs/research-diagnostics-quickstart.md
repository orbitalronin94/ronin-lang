# Inicio práctico: diagnósticos de diseño e identificabilidad

Estas APIs son herramientas de investigación complementarias al runtime de sistemas RONIN. Trabajan sobre observaciones o sensibilidades suministradas por el usuario; no sustituyen el solver ni prueban por sí solas identificabilidad estructural global.

Instalación desde la raíz del repositorio:

```bash
python -m pip install -e .
```

## 1. Diagnóstico local desde un Jacobiano

Usa esta API cuando ya tengas la matriz de sensibilidades evaluada en parámetros típicos. Cada fila es una observación y cada columna un parámetro.

```python
from ronin import diagnose_jacobian

report = diagnose_jacobian(
    [
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
    ],
    weights=[1.0, 4.0, 1.0],
    parameter_names=("clearance", "volume"),
    parameter_scales=(0.5, 3.0),
)

print(report.local_rank)
print(report.fim_condition_number)
print(report.weak_directions)
```

Los pesos son precisiones diagonales de observación. Las escalas definen coordenadas paramétricas adimensionales. El informe separa rango local, condición y direcciones débiles; deja structural_status como not_assessed y practical_status como not_calibrated porque no dispone de un modelo global ni de umbrales calibrados para tu dominio.

## 2. Elegir observaciones con D-óptimo

Cada fila del Jacobiano representa una observación candidata: por ejemplo, una hora de muestreo. El algoritmo greedy elige el subconjunto que aumenta más el log-determinante de la FIM regularizada normalizada.

```python
from ronin import d_optimal_design

candidate_sensitivities = [
    [1.0, 0.0],
    [0.0, 1.0],
    [1.0, 1.0],
    [1.0, -1.0],
]

design = d_optimal_design(
    candidate_sensitivities,
    n_samples=2,
    parameter_names=("x", "y"),
    ridge=1e-12,
)

print(design.selected_indices)
print(design.log_determinant)
print(design.local_information.local_rank)
```

Los índices son posiciones 0-based de las filas originales. El ridge es adimensional y actúa sobre la FIM normalizada. Compara scores solo con la misma parametrización, escalas, pesos y ridge. La salida incluye el diagnóstico local del subconjunto seleccionado: si el diseño sigue siendo rank-deficient, el algoritmo lo muestra en lugar de ocultarlo.

D-óptimo es un criterio de diseño local; no corrige una no-identificabilidad estructural.

## 3. Índices Sobol de primer orden

Esta API calcula el estimador de Saltelli a partir de salidas de modelo ya evaluadas. No genera muestras ni ejecuta el modelo.

```python
from ronin import sobol_first_order

f_a = [0.2, 1.3, -0.4, 2.1, 0.9]
f_b = [1.2, -0.2, 0.7, 1.9, -1.0]
f_ab = [
    [0.5, 1.0, 0.3, 2.5, 0.4],  # A_B^1
    [1.4, -0.1, 0.8, 1.2, -0.6],  # A_B^2
]

report = sobol_first_order(f_a, f_b, f_ab)
print(report.first_order_indices)
print(report.sample_count)
```

Cada fila de f_ab corresponde a un parámetro y debe contener las salidas obtenidas con la matriz híbrida A_B^i correspondiente. A y B deben ser muestras independientes de las distribuciones de parámetros declaradas. Los índices se devuelven sin recortar a [0,1]: valores fuera de ese intervalo pueden aparecer por error de muestreo o por un diseño insuficiente.

La API informa solo efectos de primer orden. No calcula interacciones de segundo orden, intervalos de confianza ni decide si el número de muestras es suficiente.

## 4. Diseño Hill antes del ajuste

Cuando el modelo de observación sea la respuesta Hill y conozcas K, alpha_h, el ruido y los valores de Omega:

```python
from ronin import diagnose_hill_design

report = diagnose_hill_design(
    omega=[0.01, 0.1, 1.0, 10.0],
    K=1.0,
    alpha_h=1.5,
    sigma=0.05,
)

print(report.local_rank)
print(report.singular_values)
print(report.weak_direction)
print(report.warnings)
```

El diagnóstico usa coordenadas log(K), log(alpha_h) y ruido gaussiano aditivo homoscedástico sobre la respuesta Hill. No debe extrapolarse a otro modelo de error sin recalcular las sensibilidades.

### Selección D-óptima directa para una curva Hill

Si tus observaciones candidatas están expresadas como valores de Omega para una respuesta Hill, puedes pedir a RONIN que derive las sensibilidades respecto a log(K) y log(alpha_h) y seleccione el subconjunto:

```python
from ronin import d_optimal_hill_design

design = d_optimal_hill_design(
    omega_candidates=[0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
    n_samples=3,
    K=1.0,
    alpha_h=1.5,
    sigma=0.05,
)

print(design.selected_omega)
print(design.design.local_information.local_rank)
print(design.warnings)
```

La derivada usa coordenadas log(K) y log(alpha_h). Se asume ruido gaussiano aditivo homoscedástico; como sigma es común a todos los candidatos, no cambia qué subconjunto maximiza el criterio normalizado. Para ruido heteroscedástico usa la API genérica d_optimal_design con pesos por observación.

## 5. SIR temprano con subreporte

La API SIR reduce el modelo a la aproximación de fase temprana y reporta combinaciones identificables, no estimaciones individuales que los datos no sostienen.

```python
from ronin import diagnose_sir_early_phase

report = diagnose_sir_early_phase(
    times=range(0, 31),
    beta=0.4,
    gamma=0.15,
    rho=0.1,
    I0=100.0,
    sigma=0.1,
)

print(report.growth_rate)
print(report.observed_amplitude)
print(report.local_information.weak_directions)
print(report.structural_status)
```

La conclusión solo aplica al modelo reducido de fase temprana con errores gaussianos independientes sobre log de casos observados. No es un diagnóstico de cualquier régimen SIR.

## 6. Reglas para interpretar los resultados

- Una FIM local de rango completo no prueba identificabilidad estructural global.
- Una FIM mal condicionada depende de escalas, parametrización, pesos y diseño de observación.
- D-óptimo optimiza un diseño local; no elimina degeneraciones estructurales.
- Sobol de primer orden no incluye interacciones ni sustituye análisis de segundo orden.
- Bootstrap requiere observaciones, modelo de error y un procedimiento de ajuste definidos. RONIN no devuelve intervalos bootstrap hasta implementar ese estimador.
- Los resultados de ejemplos sintéticos son demostraciones del algoritmo, no validación empírica de un dominio.

Para el contrato matemático, supuestos y auditoría crítica de los Papers, consulta [integración de investigación sobre identificabilidad](research-integration-identifiability.md).