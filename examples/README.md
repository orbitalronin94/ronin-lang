# Ejemplos de RONIN 1.1

**Documentación principal en castellano. English version follows below.**

## Ejemplos ejecutables

- `maquinas.ronin`: caso de aceptación PUSFRE.
- `maquinas_ces.ronin`: extensión CES.
- `pesca.ronin`: escenario base de cinco agentes.
- `degeneracy_active.ronin`: rango Ω estrecho; degeneración K–α activa.
- `degeneracy_inactive.ronin`: rango Ω superior a tres órdenes completos.

El documento fuente también bosqueja NeuralScaling (46 modelos) y FamaFrench (720 observaciones mensuales), pero ambos ejemplos contienen puntos suspensivos en lugar de todos los registros. El extracto NeuralScaling además proporciona valores de phi y psi superiores a 1, aunque el mismo documento limita ambos a [0,1]. No sustituimos esos datos por observaciones sintéticas: siguen siendo plantillas hasta que se faciliten los datasets y se resuelva la contradicción de rangos.

## Ejecutar

Desde la raíz del repositorio:

```bash
ronin check examples/maquinas.ronin
ronin solve examples/maquinas.ronin
ronin solve examples/maquinas_ces.ronin
ronin simulate examples/pesca.ronin --steps 100 --seed 42
```

---

# RONIN 1.1 examples (English)

Runnable fixtures:

- `maquinas.ronin`: PUSFRE acceptance case.
- `maquinas_ces.ronin`: CES extension.
- `pesca.ronin`: five-agent baseline.
- `degeneracy_active.ronin` and `degeneracy_inactive.ronin`: active and inactive K–alpha degeneracy cases.

The supplied NeuralScaling and FamaFrench examples are incomplete templates, not runnable datasets. No synthetic observations are substituted for the missing records.
