# TASK-04 — Reservas transaccionales sin solapamientos

## Resultado esperado

Crear reservas válidas con una respuesta clara ante conflictos y utilizar la garantía PostgreSQL ya instalada para impedir dobles reservas aun bajo concurrencia.

## Estado de la infraestructura

La migración ya aplicada es:

```text
migrations/versions/20260920_01_reservation_integrity.py
```

Implementa `reservas.fecha_fin` como columna generada en UTC y la restricción `ex_reservas_peluquero_horario_activo`. Esta TASK ya no debe crear otra exclusión duplicada; debe implementar el caso de uso y traducir el conflicto de persistencia a `ConflictError`.

## Archivos

```text
app/modules/bookings/router.py
app/modules/bookings/schemas.py
app/modules/bookings/service.py
```

## Contratos separados por actor

Un cliente autenticado no debe enviar `cliente_id`; se obtiene de su sesión para evitar IDOR. Una reserva telefónica del administrador usa un comando distinto.

```python
"""Input and output contracts for appointment use cases."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClientBookingCreate(BaseModel):
    """Appointment requested by the currently authenticated client."""

    servicio_id: int
    peluquero_id: int
    fecha_inicio: datetime
    notas_cliente: str | None = Field(default=None, max_length=2000)


class AdminBookingCreate(ClientBookingCreate):
    """Manual appointment created by an administrator for one client."""

    cliente_id: int
    canal_reserva: str = "TELEFONO"


class BookingResponse(BaseModel):
    """Stable API representation of one persisted appointment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    servicio_id: int
    peluquero_id: int
    fecha_inicio: datetime
    duracion_minutos: int
    estado: str
    canal_reserva: str
```

## Prevalidación amigable

En `app/modules/bookings/service.py`, usar la duración almacenada en cada reserva existente, no la duración solicitada para todas:

```python
"""Transactional use cases for appointment booking."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.services.shared.domain_types import BookingStatus
from app.modules.services.shared.models import Booking

ACTIVE_BOOKING_STATES = tuple(
    status.value
    for status in BookingStatus
    if status
    not in {
        BookingStatus.ATTENDED,
        BookingStatus.NO_SHOW,
        BookingStatus.CANCELLED,
    }
)


async def has_overlap(
    session: AsyncSession,
    *,
    hairdresser_id: int,
    start: datetime,
    duration_minutes: int,
) -> bool:
    """Detect an existing active reservation intersecting the requested range."""
    requested_end = start + timedelta(minutes=duration_minutes)
    conflict = await session.scalar(
        select(Booking.id)
        .where(
            Booking.peluquero_id == hairdresser_id,
            Booking.estado.in_(ACTIVE_BOOKING_STATES),
            Booking.fecha_inicio < requested_end,
            Booking.fecha_fin > start,
        )
        .limit(1)
    )
    return conflict is not None
```

Esta prevalidación mejora el mensaje al usuario, pero sola no evita una carrera entre dos requests simultáneos.

## Garantía en PostgreSQL

La garantía ya está instalada mediante una migración separada. No editar la migración inicial ni crear otra restricción equivalente. Para verificarla:

```bash
alembic current
psql -d afterlook -c "\d reservas"
```

El resultado esperado incluye `20260920_01 (head)`, la columna generada `fecha_fin` y el índice de exclusión `ex_reservas_peluquero_horario_activo`.

El servicio debe capturar `IntegrityError`, inspeccionar el nombre de la restricción y convertir solo ese caso en `ConflictError`. Otros errores de integridad se vuelven a lanzar.

## Reglas obligatorias

- Cliente existente y cuenta `ACTIVA`.
- Servicio activo.
- Usuario existente, activo, con rol `PELUQUERO` y servicio asignado.
- Inicio alineado a bloques de 30 minutos.
- Fecha futura y timezone-aware.
- Rango dentro de disponibilidad y fuera de bloqueos.
- Creación de `historial_reservas` en la misma transacción.
- Commit controlado por el caso de uso; notificaciones y Calendar quedan pendientes.

## Checklist

- [ ] El cliente no puede reservar para otro `cliente_id`.
- [ ] La prevalidación considera la duración de cada reserva existente.
- [ ] PostgreSQL impide el solapamiento bajo concurrencia.
- [ ] Los conflictos se traducen a `ConflictError`.
- [ ] Reserva e historial se confirman o revierten juntos.
- [ ] Calendar no participa en la transacción principal.
