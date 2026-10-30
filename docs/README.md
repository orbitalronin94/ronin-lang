# Documentación de RONIN 1.1

La documentación canónica de este repositorio se mantiene **primero en castellano**. Los archivos .en.md son resúmenes de acompañamiento en inglés, no traducciones literales completas; el texto fuente completo se conserva en los documentos españoles.

- [Tutorial para mortales](tutorial.md) · [English companion](tutorial.en.md)
- [Especificación formal, secciones 0–14](spec.md) · [English companion](spec.en.md)
- [Arquitectura y extensión del compilador](compiler.md) · [English companion](compiler.en.md)
- [Apéndice matemático CES-Saturada](family.md) · [English companion](family.en.md)
- [Cobertura y límites de implementación](source-coverage.md)

## Notas editoriales importantes

1. El documento maestro adjunto declara que los ejemplos 1–100 se conservan de una versión anterior, pero no incluye sus cuerpos.
2. La semántica de CES para lambda tendiendo a cero aparece con formulaciones incompatibles en distintas partes del documento: la declaración normativa inicial define el límite geométrico; N.2.3 afirma recuperación de PUSFRE. La implementación Python sigue la media geométrica CES, y la diferencia queda señalada para resolución editorial.
3. Las secciones de Rust y Office describen arquitectura y fragmentos de implementación; no equivalen a backends completos y conformes.
4. Los ejemplos con agentes/datasets omitidos se identifican como plantillas parser-only.
