# TASK-06 — Google Calendar desacoplado e idempotente

## Resultado esperado

Una reserva confirmada crea un trabajo pendiente de sincronización. Un worker llama a Google Calendar después del commit y registra éxito o error sin invalidar la reserva.

## Dependencias

Completar TASK-04 y TASK-05. El login de TASK-02 no otorga automáticamente permisos de Calendar; el consentimiento debe ser explícito y con scopes mínimos.

## Archivos

```text
app/modules/integrations/google_calendar/port.py
app/modules/integrations/google_calendar/adapter.py
app/modules/integrations/google_calendar/service.py
app/modules/integrations/google_calendar/worker.py
```

## Puerto pequeño — ISP y DIP

En `port.py`:

```python
"""Provider-independent port used by Calendar synchronization use cases."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CalendarEventDraft:
    """Provider-neutral data required to create one calendar event."""

    idempotency_key: str
    summary: str
    starts_at: datetime
    ends_at: datetime


class CalendarPort(Protocol):
    """Minimal operations required from an external calendar provider."""

    async def create_event(self, event: CalendarEventDraft) -> str:
        """Create or recover one event and return its external identifier."""
        ...

    async def cancel_event(self, external_id: str) -> None:
        """Cancel one external event without changing the local reservation."""
        ...
```

## Flujo confiable

1. La transacción de reserva crea `eventos_calendario` con estado `PENDIENTE`.
2. La reserva se confirma en PostgreSQL.
3. Un worker busca pendientes usando bloqueo `FOR UPDATE SKIP LOCKED`.
4. El worker llama al puerto Calendar fuera de la transacción de reserva.
5. Guarda `evento_externo_id` y estado `SINCRONIZADO`.
6. Ante error, guarda `FALLIDO`, detalle sanitizado y permite reintento con backoff.

La combinación `(reserva_id, proveedor)` ya es única y funciona como base de idempotencia local. El adaptador debe buscar/reutilizar el evento externo antes de crear otro durante un reintento incierto.

## Servicio de sincronización

```python
"""Use cases for reliable synchronization of pending calendar events."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.integrations.google_calendar.port import CalendarPort
from app.modules.services.shared.models import CalendarEvent


async def synchronize_event(
    session: AsyncSession,
    calendar: CalendarPort,
    event: CalendarEvent,
) -> None:
    """Synchronize one pending event and persist the provider result."""
    # Load reservation data before calling the provider.
    # Commit/close the claim transaction before external I/O.
    # Call calendar.create_event() with a stable idempotency key.
    # Persist SINCRONIZADO or FALLIDO in a new short transaction.
```

El pseudocódigo es intencional: el mecanismo de worker debe elegirse antes de implementar (CLI programada, cola de tareas o job runner). No se debe fingir confiabilidad con un `BackgroundTasks` en memoria si perder el proceso implica perder el trabajo.

## Seguridad

- Scopes mínimos de Calendar y consentimiento separado.
- Refresh tokens cifrados en reposo o almacenados en un gestor de secretos.
- Nunca registrar tokens ni respuestas completas del proveedor.
- Revocar acceso y marcar sincronizaciones pendientes cuando el usuario desconecte Calendar.

## Checklist

- [ ] Calendar depende de un puerto, no del caso de uso de reservas.
- [ ] La reserva se guarda aunque Google falle.
- [ ] El trabajo pendiente sobrevive a reinicios.
- [ ] Los reintentos no duplican eventos.
- [ ] El worker puede ejecutarse en paralelo sin tomar el mismo trabajo.
- [ ] Existen pruebas con `FakeCalendarPort`.
- [ ] Tokens y errores sensibles no aparecen en logs.
