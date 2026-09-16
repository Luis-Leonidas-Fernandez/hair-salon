# ADR-007: Validar reglas de negocio antes de implementar

## Estado

Aceptado

## Contexto

Ya existen requisitos no funcionales, modelos conceptual/lógico/físico, documento de desajuste objeto-relacional y guía de reunión. Sin embargo, varias reglas siguen siendo supuestos técnicos.

Las reglas de negocio reales de la peluquería pueden cambiar decisiones sobre servicios, duración, elección de peluquero, cancelaciones, recordatorios e integraciones.

## Decisión

Antes de implementar, coordinar una reunión de validación con la peluquería y cerrar preguntas puntuales.

La reunión debe validar:

- servicios iniciales;
- duración y precio;
- horarios reales;
- funcionamiento de los dos peluqueros;
- elección o asignación de peluquero;
- política de cancelación y no asistencia;
- datos mínimos del cliente;
- recordatorios;
- integraciones dentro o fuera del MVP.

## Consecuencias

- Las decisiones técnicas quedan ancladas en reglas reales del negocio.
- Los ADR pueden pasar de `Propuesto` a `Aceptado` después de la reunión.
- Si aparecen reglas nuevas, se actualizan requisitos y modelos antes de programar.
- Se evita construir rápido algo incorrecto. Rápido pero mal no sirve, especialmente en reservas.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Implementar directamente con supuestos | Aumenta riesgo de rehacer modelo, pantallas y lógica de agenda. |
| Validar solo por mensajes informales | Puede dejar ambigüedades críticas sin registrar. |

## Evidencia relacionada

- `docs/phase_01/validations/v1.1/Objetivos_reunion_validacion_Peluqueria_Sergio_v1.1.md`
