# ADR-002: Separar clientes y usuarios internos

## Estado

Aceptado

## Contexto

El sistema tiene tres tipos de actores iniciales:

- Clientes que reservan turnos con Google.
- Dos peluqueros que atienden turnos.
- Un administrador que configura servicios, horarios y reservas.

Aunque todos pueden tener identidad digital, no cumplen el mismo rol operativo.

## Decisión

Separar `clientes` de `usuarios` internos.

- `clientes` representa personas que reservan turnos.
- `usuarios` representa actores internos: administrador y peluqueros.
- `roles` define permisos internos como `ADMIN` y `PELUQUERO`.

## Consecuencias

- La autenticación de clientes no se mezcla con permisos administrativos.
- La agenda puede asociar reservas a un `peluquero_id` de la tabla `usuarios`.
- El panel administrativo puede evolucionar sin contaminar el modelo de clientes.
- Si en el futuro un cliente también trabaja en la peluquería, habrá que definir una regla de vinculación entre ambas identidades.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Una sola tabla `usuarios` para todos | Mezcla permisos internos con identidad de cliente y puede complicar reglas de seguridad. |
| Clientes sin persistencia propia | Impide historial por cliente, bloqueos y reportes de no asistencia. |

## Evidencia relacionada

- `docs/phase_01/data-modeling/modelado/modelo-logico.png`
- `docs/phase_01/data-modeling/modelado/modelo-fisico.png`
