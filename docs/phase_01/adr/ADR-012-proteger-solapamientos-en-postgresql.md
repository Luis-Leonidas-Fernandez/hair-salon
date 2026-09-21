# ADR-012: Proteger los solapamientos de reservas en PostgreSQL

## Estado

Aceptado

## Contexto

Una validación en Python o en el frontend no alcanza para evitar dos reservas simultáneas para el mismo peluquero. Dos solicitudes concurrentes pueden pasar la validación antes de que cualquiera confirme su transacción.

## Decisión

Delegar la invariancia final a PostgreSQL mediante:

- `reservas.fecha_fin` como columna generada desde `fecha_inicio` y `duracion_minutos`;
- normalización a UTC para que la expresión generada sea inmutable;
- extensión `btree_gist`;
- exclusión GiST `ex_reservas_peluquero_horario_activo` para estados que ocupan agenda.

El backend mantiene una prevalidación amigable, pero captura el conflicto de PostgreSQL como `ConflictError` cuando se implemente el caso de uso.

## Consecuencias

- La base protege el sistema incluso bajo concurrencia.
- Canceladas, asistidas y no asistidas no bloquean nuevos turnos.
- La migración debe ejecutarse antes de crear reservas reales.
- PostgreSQL pasa a ser responsable de esta regla de integridad, no el frontend.

## Alternativas consideradas

| Alternativa | Motivo para no elegirla |
| --- | --- |
| Validar solo en frontend | No protege API ni concurrencia. |
| Validar solo en backend | Dos transacciones concurrentes aún pueden competir. |
| Guardar solo fecha de inicio | No permite representar el rango real ocupado. |

## Evidencia relacionada

- `migrations/versions/20260920_01_reservation_integrity.py`
- `app/modules/services/shared/models.py`
- `tests/test_database_integrity.py`
- `docs/phase_01/implementation/Estado_implementacion_Peluqueria_Sergio_v1.2.md`
