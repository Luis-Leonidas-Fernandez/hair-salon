# ADR-005: Usar estados explícitos de reserva

## Estado

Aceptado

## Contexto

Las reservas necesitan representar su ciclo de vida. No alcanza con guardar fecha y cliente: también hay que saber si el turno está pendiente, en espera, agendado, reservado, confirmado, cancelado, asistido o si el cliente no asistió.

La validación de negocio mencionó varios nombres de estado. Algunos pueden parecer similares, pero no conviene descartarlos sin implementar primero un catálogo controlado y reglas claras de transición.

## Decisión

Usar estados explícitos y normalizados para `reservas.estado`:

- `PENDIENTE`
- `EN_ESPERA`
- `AGENDADA`
- `RESERVADA`
- `CONFIRMADA`
- `ASISTIO`
- `NO_ASISTIO`
- `CANCELADA`

El modelo físico debe reforzar esos valores con una restricción `CHECK` o un catálogo controlado. `CANCELADA` se mantiene aunque no haya sido listada en la respuesta de estados, porque la validación confirmó cancelaciones.

## Consecuencias

- Los reportes pueden distinguir turnos atendidos, cancelados y no asistidos.
- Las notificaciones pueden depender del estado de la reserva.
- La disponibilidad debe decidir qué estados ocupan agenda.
- El equipo deberá definir transiciones permitidas entre estados antes de implementar la lógica de agenda.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Texto libre | Genera variantes como “cancelado”, “Cancelada”, “no vino” y rompe reportes. |
| Booleanos separados | Puede producir combinaciones contradictorias. |

## Evidencia relacionada

- `docs/phase_01/data-modeling/modelado/modelo-fisico.png`
- `docs/phase_01/validations/v1.1/Objetivos_reunion_validacion_Peluqueria_Sergio_v1.1.md`


## Validación de negocio

La reunión confirmó los siguientes términos usados por la peluquería: agendado, reservado, confirmado, asiste, no asistió, pendiente y en espera. La decisión técnica los normaliza para evitar texto libre y variantes inconsistentes.
