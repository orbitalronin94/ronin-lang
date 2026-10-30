# Documentación de RONIN Runtime v0.1 · MDES v0.5

La documentación canónica se mantiene **primero en castellano**. MDES v0.5 es la versión de referencia de la especificación; RONIN Runtime v0.1 es el estado actual del software. No son el mismo número de versión.

## Empezar

- [Tutorial para mortales](tutorial.md) · [English companion](tutorial.en.md)
- [Roadmap de v0.1 a v1.0](roadmap.md)
- [Especificación formal de MDES](spec.md) · [English companion](spec.en.md)
- [Matriz de trazabilidad y conformidad MDES v0.5](conformance-matrix.md) — IDs, estado Python/Rust, pruebas y bloqueos.
- [Cobertura y límites de implementación](source-coverage.md)

## Especificación y arquitectura

- [Arquitectura y extensión del compilador](compiler.md) · [English companion](compiler.en.md)
- [Apéndice matemático CES-Saturada](family.md) · [English companion](family.en.md)
- [Parte V — Runtime de referencia Python](python-runtime-spec.md) · [English summary](python-runtime-spec.en.md)
- [Parte VI — Especificación del backend Rust](rust-backend-spec.md) · [English summary](rust-backend-spec.en.md)
- [Parte VII — Especificación de RONIN Office](office-spec.md) · [English summary](office-spec.en.md)
- [Parte VIII — Visión de futuro](vision.md) · [English summary](vision.en.md)
- [Anexo normativo](normative-annex.md) · [English summary](normative-annex.en.md)

## Notas editoriales y de conformidad

1. El documento maestro declara que los ejemplos 1–100 se conservan de una versión anterior, pero no incluye sus cuerpos. No se reconstruyen por conjetura.
2. La semántica CES para lambda tendiendo a cero presenta formulaciones incompatibles en distintas partes del material. La implementación actual sigue el límite geométrico y la discrepancia permanece documentada para resolución normativa.
3. Las especificaciones Rust y Office describen objetivos que no deben confundirse con la cobertura implementada. El estado actual se resume en [source-coverage.md](source-coverage.md).
4. Los ejemplos con agentes, variables o datasets omitidos se identifican como plantillas parser-only cuando corresponde.

El castellano es el idioma principal; los archivos `.en.md` son resúmenes de acompañamiento, no traducciones literales completas. El material fuente se conserva en sus documentos españoles.
