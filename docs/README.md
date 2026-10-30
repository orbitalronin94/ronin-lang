# Documentación de RONIN 1.1

La documentación canónica de este repositorio se mantiene **primero en castellano**. Los archivos .en.md son resúmenes de acompañamiento en inglés, no traducciones literales completas; el texto fuente completo se conserva en los documentos españoles.

- [Tutorial para mortales](tutorial.md) · [English companion](tutorial.en.md)
- [Especificación formal, secciones 0–14](spec.md) · [English companion](spec.en.md)
- [Arquitectura y extensión del compilador](compiler.md) · [English companion](compiler.en.md)
- [Apéndice matemático CES-Saturada](family.md) · [English companion](family.en.md)
- [Parte V — Runtime de referencia Python](python-runtime-spec.md) · [English summary](python-runtime-spec.en.md)
- [Parte VI — Especificación del backend Rust](rust-backend-spec.md) · [English summary](rust-backend-spec.en.md)
- [Parte VII — Especificación de RONIN Office](office-spec.md) · [English summary](office-spec.en.md)
- [Parte VIII — Visión de futuro](vision.md) · [English summary](vision.en.md)
- [Anexo normativo v1.1](normative-annex.md) · [English summary](normative-annex.en.md)
- [Cobertura y límites de implementación](source-coverage.md)

## Notas editoriales importantes

1. El documento maestro adjunto declara que los ejemplos 1–100 se conservan de una versión anterior, pero no incluye sus cuerpos.
2. La semántica de CES para lambda tendiendo a cero aparece con formulaciones incompatibles en distintas partes del documento: la declaración normativa inicial define el límite geométrico; N.2.3 afirma recuperación de PUSFRE. La implementación Python sigue la media geométrica CES, y la diferencia queda señalada para resolución editorial.
3. Las especificaciones completas de Rust y Office se han separado en documentos propios. El workspace Rust sigue siendo un esqueleto; Office es un prototipo local con paneles básicos, no la suite completa.
4. Los ejemplos con agentes/datasets omitidos se identifican como plantillas parser-only.
