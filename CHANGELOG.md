# Changelog de RONIN Runtime

Los cambios de MDES y del runtime se versionan por separado. Este archivo registra cambios del software; no implica conformidad integral con MDES v0.5.

## Unreleased — candidato RONIN Runtime 0.5.0

> Borrador de release notes. No existe todavía tag, paquete ni GitHub Release v0.5.0. La versión publicada en los metadatos del repositorio sigue siendo 0.1.0.

### Añadido
- Suite determinista de paridad Python/Rust para 80 sistemas solver (16 por cada uno de PUSFRE, CES, Hill, CES-Hill y full-order-1).
- Suite determinista de paridad de simulación para 15 sistemas generados, 24 pasos por sistema y semillas fijas.
- Alcance explícito para las capacidades de investigación: FIM/Jacobiano, SIR, D-óptimo y Sobol no forman parte del contrato estable candidato.
- Comprobaciones CI de distribución: construcción de sdist/wheel, instalación del wheel en un entorno virtual aislado, y compilación/smoke del binario Rust optimizado con `--release --locked`.

### Corregido / aclarado
- `debt` se representa como `null` cuando no existe estimador; no debe interpretarse como deuda cero.
- La documentación de trazabilidad distingue evidencia de parser, validación y ejecución, y explicita las capacidades fuera del perfil.

### Límites conocidos del candidato
- No se declara conformidad integral con MDES v0.5.
- Deuda y bootstrap CI no están implementados; sus resultados permanecen `null`.
- El perfil de lenguaje es un subconjunto declarativo; no incluye lenguaje general, módulos, macros ni concurrencia.
- La compatibilidad Python/Rust solo se afirma para los casos y contratos enumerados.
- El smoke de distribución se ha verificado en Ubuntu CI; no se afirma soporte probado en Windows/macOS.
- El IR v1 se emite y valida, pero no existe importador IR→RONIN ni round-trip.
- La propuesta de perfil Runtime v0.5 requiere aprobación explícita y los bloqueos normativos OPEN-001…OPEN-007 siguen sujetos a fuente, ADR o exclusión formal.

### Pendiente antes de publicar
- Cerrar revisión semántica de las 62 filas I/P de la matriz.
- Aprobar el perfil de compatibilidad y resolver/excluir los bloqueos normativos.
- Integrar el caso de proyecto de 1.000 agentes de PR #96 y repetir CI en el SHA final.
- Preparar RC, guía de migración final, artefactos y checksums.
- Publicar tag y GitHub Release solo tras cumplir los gates C7/C8.
