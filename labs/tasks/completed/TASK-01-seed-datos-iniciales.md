# TASK-01 — Seed idempotente de datos iniciales

## Resultado esperado

Una ejecución crea el administrador, dos peluqueros, servicios, capacidades y disponibilidad base. Ejecuciones posteriores no duplican registros.

> `clientes` es una entidad separada de `usuarios`; por eso los roles iniciales son únicamente `ADMIN` y `PELUQUERO`.

> **Precios pendientes:** no se cargan ni se exponen precios comerciales hasta contar con el visto bueno de los peluqueros. El valor técnico por defecto del esquema no representa un precio real ni habilita una pantalla de precios.

## Archivo a crear

```text
scripts/seed_initial_data.py
```

## Código sugerido

```python
"""Load idempotent reference data required by the After Look MVP.

This development seed creates internal roles, staff users, services,
staff-service capabilities, and weekly availability. It is safe to rerun
because every lookup uses a database uniqueness rule as its identity.
"""

import asyncio
from datetime import time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import AsyncSessionFactory
from app.modules.services.shared.models import (
    Availability,
    Role,
    Service,
    User,
    UserService,
)


async def get_or_create_role(
    session: AsyncSession, name: str, description: str
) -> Role:
    """Return the named internal role, creating it when absent."""
    role = await session.scalar(select(Role).where(Role.nombre == name))
    if role is None:
        role = Role(nombre=name, descripcion=description)
        session.add(role)
        await session.flush()
    return role


async def get_or_create_user(
    session: AsyncSession, *, name: str, email: str, role: Role
) -> User:
    """Return an internal user identified by Google email or create it."""
    user = await session.scalar(select(User).where(User.email_google == email))
    if user is None:
        user = User(nombre_completo=name, email_google=email, rol=role)
        session.add(user)
        await session.flush()
    return user


async def get_or_create_service(
    session: AsyncSession, *, name: str, service_type: str
) -> Service:
    """Return a service or create it with a non-commercial technical price."""
    service = await session.scalar(select(Service).where(Service.nombre == name))
    if service is None:
        service = Service(
            nombre=name,
            tipo_servicio=service_type,
            duracion_minutos=60,
            # `precio_base` is intentionally omitted: the schema default is technical only.
            activo=True,
        )
        session.add(service)
        await session.flush()
    return service


async def ensure_capability(
    session: AsyncSession, *, user: User, service: Service
) -> None:
    """Assign one service to one hairdresser without duplicating the relation."""
    capability = await session.scalar(
        select(UserService).where(
            UserService.usuario_id == user.id,
            UserService.servicio_id == service.id,
        )
    )
    if capability is None:
        session.add(UserService(usuario=user, servicio=service, activo=True))


async def ensure_weekly_availability(
    session: AsyncSession, *, hairdresser: User
) -> None:
    """Create Monday-to-Saturday availability from 09:30 through 22:00."""
    for weekday in range(1, 7):
        availability = await session.scalar(
            select(Availability).where(
                Availability.usuario_id == hairdresser.id,
                Availability.dia_semana == weekday,
                Availability.hora_desde == time(9, 30),
                Availability.hora_hasta == time(22, 0),
            )
        )
        if availability is None:
            session.add(
                Availability(
                    usuario=hairdresser,
                    dia_semana=weekday,
                    hora_desde=time(9, 30),
                    hora_hasta=time(22, 0),
                    activa=True,
                )
            )


async def seed() -> None:
    """Commit all initial data atomically or roll back everything on failure."""
    async with AsyncSessionFactory.begin() as session:
        admin_role = await get_or_create_role(
            session, "ADMIN", "Administración general del sistema"
        )
        hairdresser_role = await get_or_create_role(
            session, "PELUQUERO", "Gestión de agenda y atención"
        )

        await get_or_create_user(
            session,
            name="Administrador",
            email="admin@afterlook.local",
            role=admin_role,
        )
        hairdressers = (
            await get_or_create_user(
                session,
                name="Peluquero 1",
                email="peluquero1@afterlook.local",
                role=hairdresser_role,
            ),
            await get_or_create_user(
                session,
                name="Peluquero 2",
                email="peluquero2@afterlook.local",
                role=hairdresser_role,
            ),
        )
        services = (
            await get_or_create_service(
                session,
                name="Corte de cabello",
                service_type="PELUQUERIA",
            ),
            await get_or_create_service(
                session,
                name="Barbería",
                service_type="BARBERIA",
            ),
        )

        for hairdresser in hairdressers:
            await ensure_weekly_availability(session, hairdresser=hairdresser)
            for service in services:
                await ensure_capability(session, user=hairdresser, service=service)


if __name__ == "__main__":
    asyncio.run(seed())
```

## Por qué está diseñado así

- **SRP:** cada función crea un solo tipo de dato.
- **Transacción única:** `AsyncSessionFactory.begin()` confirma todo o revierte todo.
- **Idempotencia:** usa claves únicas existentes; no depende de IDs fijos.
- **Modelo correcto:** clientes no se mezclan con usuarios internos.

## Ejecución y verificación

```bash
python scripts/seed_initial_data.py
python scripts/seed_initial_data.py
```

```sql
SELECT nombre FROM roles ORDER BY nombre;
SELECT nombre_completo, email_google FROM usuarios ORDER BY id;
SELECT nombre FROM servicios ORDER BY id;
SELECT usuario_id, servicio_id FROM usuarios_servicios ORDER BY 1, 2;
SELECT usuario_id, COUNT(*) FROM disponibilidades GROUP BY usuario_id;
```

## Checklist

- [ ] Solo existen los roles `ADMIN` y `PELUQUERO` para usuarios internos.
- [ ] Hay un administrador y exactamente dos peluqueros de desarrollo.
- [ ] Ambos peluqueros tienen servicios asignados.
- [ ] Ambos tienen horario de lunes a sábado.
- [ ] Ejecutar el script dos veces no cambia las cantidades.
- [ ] Los emails `.local` se reemplazan antes de un ambiente real.
- [ ] Los precios comerciales permanecen pendientes de aprobación y no se exponen al cliente.
