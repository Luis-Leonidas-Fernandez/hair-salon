# ADR-003: Modelar reserva como entidad central

## Estado

Aceptado

## Contexto

La acción principal del sistema es reservar un turno para un servicio con un peluquero. Esa acción conecta cliente, servicio, disponibilidad, estado, historial y notificaciones.

Si la reserva no queda como núcleo del modelo, las reglas de negocio se dispersan y se vuelve más difícil evitar solapamientos o reconstruir el historial.

## Decisión

Modelar `reservas` como entidad central del sistema.

Una reserva referencia:

- `cliente_id`
- `servicio_id`
- `peluquero_id`
- `fecha_inicio`
- `duracion_minutos`
- `estado`
- `canal_reserva`

## Consecuencias

- La agenda diaria puede consultarse desde `reservas` filtrando por peluquero y fecha.
- El historial puede depender de `reserva_id`.
- Las notificaciones pueden derivarse de reservas existentes.
- La prevención de doble turno debe diseñarse alrededor de `peluquero_id`, `fecha_inicio`, duración y estado.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Modelar agenda como entidad principal | La agenda define disponibilidad, pero la unidad de negocio confirmada es la reserva. |
| Guardar turnos como eventos sueltos | Complica estados, cancelaciones, historial y consultas operativas. |

## Evidencia relacionada

- `docs/phase_01/data-modeling/modelado/modelo-conceptual.png`
- `docs/phase_01/data-modeling/modelado/modelo-logico.png`
- `docs/phase_01/data-modeling/modelado/modelo-fisico.png`
