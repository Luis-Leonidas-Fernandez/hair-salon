# Estado de implementación — After Look v1.2

Este documento conecta el diseño aprobado con lo que ya está implementado en el proyecto. La versión v1.2 incorpora configuración centralizada, vocabularios controlados y protección de base de datos contra reservas superpuestas.

## Camino rápido

1. Activar el entorno virtual.
2. Ejecutar `ruff check app tests migrations`.
3. Ejecutar `pytest -q`.
4. Verificar la revisión de Alembic con `alembic current`.

## Etapas completadas

| Etapa | Resultado | Evidencia |
| --- | --- | --- |
| 1 | Seed inicial idempotente y validado | `scripts/seed_initial_data.py`, `tests/test_seed_validations.py` |
| 2 | Configuración centralizada desde `.env` | `app/config/settings.py`, `tests/test_settings.py` |
| 3 | Enums para vocabularios del dominio | `app/modules/services/shared/domain_types.py`, `tests/test_domain_types.py` |
| 4 | Integridad de reservas en PostgreSQL | `migrations/versions/20260920_01_reservation_integrity.py` |

## Integridad de reservas implementada

La tabla `reservas` ahora posee:

- `fecha_fin`, calculada a partir de `fecha_inicio` y `duracion_minutos`.
- La restricción `ex_reservas_peluquero_horario_activo`.
- Protección contra solapamientos para el mismo peluquero en estados activos.
- Soporte PostgreSQL `btree_gist` para la exclusión GiST.

Los estados que ocupan agenda son:

```text
PENDIENTE, EN_ESPERA, AGENDADA, RESERVADA, CONFIRMADA
```

Los estados `ASISTIO`, `NO_ASISTIO` y `CANCELADA` no bloquean nuevos turnos.

## Verificación realizada

```text
Alembic: 20260920_01 (head)
Tests: 16 passed
```

La base local `afterlook` fue revisada antes de aplicar la migración y no contenía reservas superpuestas.

## Decisiones que siguen vigentes

- Los clientes se autentican con Google OAuth.
- Google Calendar es una integración derivada; PostgreSQL sigue siendo la fuente de verdad.
- Pagos, señas y facturación quedan fuera del MVP.
- WhatsApp continúa pendiente de proveedor, costo y factibilidad.
- Los precios no se exponen hasta obtener aprobación de los peluqueros.

## ADR relacionados

- [ADR-009 — Seed idempotente y validado](../adr/ADR-009-seed-idempotente-y-validado.md)
- [ADR-010 — Configuración tipada desde el entorno](../adr/ADR-010-configuracion-tipada-desde-entorno.md)
- [ADR-011 — Vocabularios del dominio mediante enums](../adr/ADR-011-centralizar-vocabularios-del-dominio.md)
- [ADR-012 — Protección de solapamientos en PostgreSQL](../adr/ADR-012-proteger-solapamientos-en-postgresql.md)
- [ADR-013 — Estado de implementación versionado](../adr/ADR-013-versionar-el-estado-de-implementacion.md)

## Próxima etapa

Implementar los casos de uso de reservas sobre esta base, incluyendo validación de cliente activo, servicio activo, peluquero asignado, disponibilidad, bloques de 30 minutos y manejo de conflictos.
