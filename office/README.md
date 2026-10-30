# RONIN Office — prototipo local ampliado

Abre `index.html` directamente en un navegador moderno. No requiere servidor, paquetes ni conexión externa. Los datos permanecen en el navegador.

## Paneles incluidos

- **Chat local:** ayuda determinista basada en conceptos de RONIN; no es un LLM ni genera código arbitrario.
- **Sheet:** tabla sincronizada de agentes e importación/exportación CSV.
- **Optimizer:** barrido heurístico de alpha PUSFRE para maximizar la menor cuota asignada.
- **Simulator:** simulación local reproducible con deriva de medio paso, ruido gaussiano `sigma / 10` y proyección al símplex.
- **Agent Studio:** alta rápida de agentes.
- **Diagnose:** rango Ω, estado de degeneración e identificabilidad desde el motor principal.

## Límites importantes

Esto es un prototipo funcional de los flujos básicos, no la suite completa descrita en la Parte VII. Chat no usa un modelo de lenguaje; Optimizer no es un optimizador global ni ofrece restricciones avanzadas; Sheet no es un editor completo del lenguaje; no hay almacenamiento de proyectos, colaboración, historial, integración con runtime Python/Rust ni memoria temporal. Consulta [la especificación completa](../docs/office-spec.md) para el diseño normativo y sus límites.
