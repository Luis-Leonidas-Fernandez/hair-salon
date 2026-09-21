# TASK-03 — Catálogo y disponibilidad calculada

## Resultado esperado

El cliente consulta servicios activos y slots realmente reservables para un servicio y peluquero, usando zona horaria explícita y bloques de 30 minutos. Los precios no se exponen hasta contar con aprobación comercial de los peluqueros.

## Archivos

```text
app/modules/services/router.py
app/modules/services/schemas.py
app/modules/services/service.py
app/modules/services/dependencies.py
```

## Dependencia tipada de sesión

En `app/modules/services/dependencies.py`:

```python
"""Reusable FastAPI dependency aliases for the services module."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
```

Esto conserva autocompletado y evita repetir `Depends(...)` en cada endpoint.

## Contratos HTTP

En `app/modules/services/schemas.py`:

```python
"""Public HTTP contracts for services and bookable slots."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ServiceResponse(BaseModel):
    """Public representation of an active salon service."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    tipo_servicio: str
    duracion_minutos: int


class AvailableSlotResponse(BaseModel):
    """One timezone-aware slot that can fit the selected service."""

    peluquero_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
```

## Consulta del catálogo

En `app/modules/services/service.py`:

```python
"""Queries and calculations for the public service catalog."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.services.shared.models import Service


async def list_active_services(session: AsyncSession) -> list[Service]:
    """Return active services in a stable alphabetical order."""
    result = await session.scalars(
        select(Service).where(Service.activo.is_(True)).order_by(Service.nombre)
    )
    return list(result)
```

## Algoritmo de disponibilidad

El caso de uso de slots debe:

1. cargar servicio y confirmar que esté activo;
2. confirmar que el peluquero brinda ese servicio en `usuarios_servicios`;
3. cargar disponibilidad semanal y bloqueos excepcionales;
4. generar candidatos en intervalos de 30 minutos;
5. descartar candidatos que no soporten la duración completa;
6. consultar reservas activas del día en una sola query;
7. descartar cualquier intervalo que se solape;
8. convertir la salida a `America/Argentina/Buenos_Aires`.

No ejecutar una consulta por cada slot. Cargar los intervalos ocupados una vez y calcular los candidatos en memoria.

## Router delgado

```python
"""HTTP routes for the public service catalog."""

from fastapi import APIRouter

from app.modules.services.dependencies import DbSession
from app.modules.services.schemas import ServiceResponse
from app.modules.services.service import list_active_services

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
async def get_services(session: DbSession) -> list[ServiceResponse]:
    """List services that clients can currently book."""
    return await list_active_services(session)
```

## Checklist

- [ ] `GET /services` devuelve solo servicios activos.
- [ ] El peluquero debe brindar el servicio solicitado.
- [ ] Todos los datetimes son conscientes de zona horaria.
- [ ] Los slots respetan bloques de 30 minutos y la duración completa.
- [ ] Bloqueos y reservas activas eliminan slots.
- [ ] No existe N+1 al calcular disponibilidad.
- [ ] Router, contratos y reglas permanecen separados.
- [ ] La respuesta pública no expone precios hasta su aprobación comercial.
