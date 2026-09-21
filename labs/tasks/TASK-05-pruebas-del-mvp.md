# TASK-05 — Estrategia de pruebas del MVP

## Resultado esperado

Probar reglas puras, endpoints, persistencia y concurrencia sin usar la base de desarrollo ni servicios reales de Google.

## Pirámide proporcional

| Nivel | Qué protege | Ejemplos |
|---|---|---|
| Unitario | Reglas sin I/O | bloques de 30 minutos, transiciones de estado. |
| Integración | SQL y constraints | solapamientos, unicidad, rollback. |
| API | Contratos HTTP | servicios, login callback, reservas. |
| Adaptadores | Traducción externa | Google falso, errores y reintentos. |

## Infraestructura de pruebas

Crear:

```text
tests/conftest.py
tests/unit/test_booking_rules.py
tests/integration/test_booking_concurrency.py
tests/api/test_services.py
tests/api/test_bookings.py
```

La base de test debe ser distinta de `afterlook`, ejecutar migraciones y limpiarse entre pruebas. No usar SQLite: las restricciones GiST y `TIMESTAMPTZ` son comportamiento PostgreSQL.

## Cliente HTTP async

Evitar `TestClient` si la versión instalada emite deprecaciones. Usar HTTPX con transporte ASGI:

```python
"""Shared HTTP test fixtures for the FastAPI application."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def api_client():
    """Yield an async client that calls the application without a real server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client
```

## Contrato de solapamiento

```python
"""Integration tests for the no-overlap booking invariant."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.shared.errors.conflict_error import ConflictError


async def test_overlapping_booking_is_rejected(booking_service, booking_factory):
    """Reject a second active appointment intersecting the same hairdresser."""
    timezone = ZoneInfo("America/Argentina/Buenos_Aires")
    existing = await booking_factory(
        start=datetime(2026, 10, 1, 10, 0, tzinfo=timezone),
        minutes=60,
    )

    with pytest.raises(ConflictError):
        await booking_service.create(
            hairdresser_id=existing.peluquero_id,
            start=datetime(2026, 10, 1, 10, 30, tzinfo=timezone),
            service_id=existing.servicio_id,
        )
```

`booking_service` y `booking_factory` son fixtures que se implementan junto con TASK-04; no se debe dejar un `NotImplementedError` dentro de la suite.

## Prueba de concurrencia obligatoria

Lanzar dos transacciones independientes intentando reservar el mismo peluquero y horario. El resultado esperado es una reserva confirmada y un conflicto por `ex_reservas_peluquero_horario`.

## Dobles de prueba

- `FakeIdentityProvider` implementa `IdentityProvider`.
- `FakeCalendarPort` implementa `CalendarPort`.
- No mockear SQLAlchemy para pruebas de constraints; usar PostgreSQL real de test.
- No contactar Google desde CI.

## Comandos

```bash
ruff check .
python -m pytest -q
```

## Checklist

- [ ] Tests unitarios de bloques y estados.
- [ ] Tests API con HTTPX async.
- [ ] Tests de unicidad de email.
- [ ] Test de solapamiento secuencial.
- [ ] Test de dos reservas concurrentes.
- [ ] Test de rollback de reserva e historial.
- [ ] Google reemplazado por adaptadores falsos.
- [ ] Ningún test usa `afterlook` ni credenciales reales.
