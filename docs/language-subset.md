# Subconjunto técnico del parser RONIN

**Estado:** inventario técnico del comportamiento implementado; no es una decisión normativa ni la aprobación del perfil v1.0.  
**Backends:** ronin/parser.py / ronin/lexer.py y rust/src/parser.rs.  
**Evidencia:** scripts/check_parser_parity.py, tests/test_parser_strictness.py y tests Rust del parser.

Este documento describe lo que aceptan actualmente los dos parsers. No promete que el subconjunto sea la gramática completa de MDES v0.5, ni convierte las construcciones no implementadas en parte del lenguaje estable.

## 1. Forma de un archivo

Un archivo contiene cero o más declaraciones system:

~~~ronin
system Coastal = {
  parts: 2,
  resource: 100,
  agents: [
    { phi: 0.6, psi: 0.9, frequency: 0.5, role: worker },
    { phi: 0.5, psi: 0.8, frequency: 0.5 }
  ],
  params: {
    model: "hill",
    K: 1,
    alpha_h: 2
  }
}
~~~

Cada declaración requiere parts, resource y agents. params es opcional. Los nombres de sistemas y las claves de los bloques usan identificadores ASCII: letra o guion bajo inicial, seguidos de letras, dígitos o guion bajo.

## 2. Léxico y valores

- Espacios admitidos fuera de cadenas: espacio ASCII, tabulador, CR y LF. Otros caracteres de espacio Unicode, vertical tab y form feed se rechazan.
- Comentarios de línea: // hasta LF.
- Números: signo opcional, enteros/decimales y exponente decimal. inf, infinity y ∞ representan infinito positivo. NaN no es un número aceptado en campos numéricos.
- Cadenas: comillas dobles con escapes JSON (comilla, barra inversa, barra, backspace, form feed, newline, carriage return, tab y Unicode \uXXXX). Se admiten pares surrogate válidos; se rechazan surrogates aislados y controles sin escape.
- Literales true, false, null e infinitos son insensibles a mayúsculas/minúsculas en los valores.
- Un identificador desnudo usado como valor se conserva como cadena (por ejemplo, role: worker).
- Se admiten arrays y objetos anidados. Las claves de objetos pueden ser identificadores o cadenas entre comillas. Las claves duplicadas se rechazan.
- Arrays y objetos requieren comas entre elementos/campos; se admite coma final. Los campos de system, agents y params aceptan coma opcional según el parser actual.

## 3. Campos estructurales

### system

| Campo | Regla del parser |
|---|---|
| parts | Numérico, entero y mayor que cero |
| resource | Numérico; el validador semántico aplica después las restricciones de dominio |
| agents | Array de objetos de agente |
| params | Objeto opcional de parámetros conocidos |

Se rechazan campos de sistema desconocidos y campos duplicados.

### agents

Cada agente requiere phi, psi y frequency numéricos. Los demás campos se conservan como metadata, incluidos arrays y objetos anidados. Los nombres de metadata son libres, pero no pueden repetirse dentro del mismo agente.

### params

Claves reconocidas actualmente (respetando mayúsculas/minúsculas del nombre):

alpha, gamma, sigma, coexistence_delta, model, lambda, K, alpha_h, memory_order, memory_weights, degeneracy_check y omega_range_report. La clave k (minúscula) no es alias de K. Tipos, rangos y coherencia del modelo se completan en la validación semántica; el parser no implementa un sistema de tipos general.

## 4. Fuera del subconjunto actual

El parser no implementa expresiones, asignaciones generales, funciones fn, llamadas, if, bucles, plot, sentencias simulate/audit/diagnose, módulos/imports, macros ni un intérprete de programas de alto nivel. Las operaciones equivalentes que existan como CLI/API no son sintaxis del lenguaje.

Tampoco existe un importador de JSON IR v1 de vuelta a una declaración RONIN. La evidencia de IR v1 cubre compilación/exportación, parseo JSON estructural y equivalencia Python/Rust.

## 5. Límites de la evidencia

El corpus compartido verifica aceptación/rechazo en nueve archivos válidos, tres fuentes válidas inline y 28 fuentes inválidas inline. Es un corpus de regresión del subconjunto actual, no una prueba exhaustiva de la gramática MDES. Los diagnósticos se comparan por categoría y ubicación en los casos testigo; no se exige identidad textual de mensajes entre backends.

Cualquier ampliación del subconjunto debe añadir casos positivos y negativos a la paridad compartida, actualizar la matriz y documentar si cambia compatibilidad. La inclusión de construcciones de alto nivel en el perfil v1.0 requiere una decisión explícita del mantenedor y semántica normativa suficiente.
