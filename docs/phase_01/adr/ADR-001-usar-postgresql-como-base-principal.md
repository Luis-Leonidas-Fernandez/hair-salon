# ADR-001: Usar PostgreSQL como base principal

## Estado

Aceptado

## Contexto

El sistema necesita registrar clientes, servicios, peluqueros, disponibilidad, reservas, historial y notificaciones. La parte más sensible es evitar reservas duplicadas o solapadas para un mismo peluquero y horario.

El modelo físico ya está orientado a PostgreSQL con claves foráneas, índices, restricciones `CHECK`, timestamps con zona horaria y transacciones.

## Decisión

Usar PostgreSQL como base de datos principal y fuente oficial de verdad para reservas, clientes, servicios, disponibilidad e historial operativo.

## Consecuencias

- La consistencia de turnos puede apoyarse en transacciones, claves foráneas, índices y restricciones.
- Los reportes operativos pueden consultar datos relacionales sin depender de archivos externos.
- Las validaciones importantes no quedan solo en el frontend.
- El equipo debe diseñar migraciones y pruebas de integridad con cuidado.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla ahora |
| --- | --- |
| Base NoSQL | No aporta ventaja clara para un sistema de reservas con relaciones fuertes. |
| Planillas | No protegen suficientemente contra solapamientos, pérdida de historial o errores concurrentes. |
| SQLite | Puede servir para prototipos, pero PostgreSQL da mejores garantías para concurrencia y crecimiento. |

## Evidencia relacionada

- `docs/phase_01/data-modeling/modelado/modelo-fisico.png`
- `docs/phase_01/requirements/v1.1/Requisitos_no_funcionales_Peluqueria_Sergio_v1.1.md`
