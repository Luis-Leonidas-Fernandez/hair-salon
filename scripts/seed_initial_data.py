"""Create idempotent reference data required by the After Look MVP."""

import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.infrastructure.database.session import AsyncSessionFactory
from app.modules.services.shared.initial_catalog import INITIAL_SERVICES, InitialService
from app.modules.services.shared.initial_roles import INITIAL_ROLES, InitialRole
from app.modules.services.shared.models import (
    Availability,
    Booking,
    Client,
    Role,
    Service,
    User,
    UserService,
)
from app.modules.services.shared.role_types import InternalRole
from app.modules.services.shared.seed_plan import (
    BASE_WEEKLY_SCHEDULE,
    SeedIdentity,
    WeeklySchedule,
    build_seed_identities,
)
from app.modules.services.shared.seed_validations import (
    validate_existing_capability,
    validate_existing_role,
    validate_existing_service,
    validate_existing_user_role,
    validate_seed_configuration,
    validate_weekly_availability,
)


async def get_or_create_role(session: AsyncSession, *, definition: InitialRole) -> Role:
    """Return an internal role from the initial catalog, creating it when absent."""

    role = await session.scalar(
        select(Role).where(Role.nombre == definition.name.value)
    )
    validate_existing_role(role=role, definition=definition)
    if role is None:
        role = Role(
            nombre=definition.name.value,
            descripcion=definition.description,
            activo=True,
        )
        session.add(role)
        await session.flush()
    return role


async def get_or_create_user(
    session: AsyncSession, *, identity: SeedIdentity, role: Role
) -> User:
    """Return a configured internal user after checking its expected role."""

    # Remove temporary client profile if this staff identity previously logged in
    # via OAuth
    existing_client = await session.scalar(
        select(Client).where(Client.email_google == identity.email)
    )
    if existing_client is not None:
        has_bookings = await session.scalar(
            select(func.count(Booking.id)).where(
                Booking.cliente_id == existing_client.id
            )
        )
        if not has_bookings:
            await session.delete(existing_client)
            await session.flush()

    user = await session.scalar(select(User).where(User.email_google == identity.email))
    validate_existing_user_role(user=user, identity=identity, role_id=role.id)
    if user is None:
        user = User(
            nombre_completo=identity.display_name,
            email_google=identity.email,
            rol=role,
            activo=True,
        )
        session.add(user)
        await session.flush()
    return user


async def get_or_create_service(
    session: AsyncSession, *, definition: InitialService
) -> Service:
    """Return a catalog service after checking its immutable seed attributes."""

    service = await session.scalar(
        select(Service).where(Service.nombre == definition.name)
    )
    validate_existing_service(service=service, definition=definition)
    if service is None:
        service = Service(
            nombre=definition.name,
            descripcion=definition.description,
            tipo_servicio=definition.service_type.value,
            duracion_minutos=definition.duration_minutes,
            activo=True,
        )
        session.add(service)
        await session.flush()
    return service


async def ensure_capability(
    session: AsyncSession, *, user: User, service: Service
) -> None:
    """Assign a service to a hairdresser without duplicating the relation."""

    capability = await session.scalar(
        select(UserService).where(
            UserService.usuario_id == user.id,
            UserService.servicio_id == service.id,
        )
    )
    validate_existing_capability(capability=capability)
    if capability is None:
        session.add(UserService(usuario=user, servicio=service, activo=True))


async def ensure_weekly_availability(
    session: AsyncSession,
    *,
    hairdresser: User,
    schedule: WeeklySchedule,
) -> None:
    """Create the base schedule only when no conflicting schedule exists."""

    for weekday in schedule.weekdays:
        exact_schedule_exists = await validate_weekly_availability(
            session,
            hairdresser=hairdresser,
            weekday=weekday,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
        )
        if not exact_schedule_exists:
            session.add(
                Availability(
                    usuario=hairdresser,
                    dia_semana=weekday,
                    hora_desde=schedule.start_time,
                    hora_hasta=schedule.end_time,
                    activa=True,
                )
            )


async def seed() -> None:
    """Validate and commit all seed data atomically or roll back on failure."""

    configured_identities = build_seed_identities(get_settings())
    validate_seed_configuration(
        identities=configured_identities,
        initial_roles=INITIAL_ROLES,
        initial_services=INITIAL_SERVICES,
    )

    async with AsyncSessionFactory.begin() as session:
        roles = {
            definition.name: await get_or_create_role(session, definition=definition)
            for definition in INITIAL_ROLES
        }
        admin_role = roles[InternalRole.ADMIN]
        hairdresser_role = roles[InternalRole.PELUQUERO]

        admin_identity, *hairdresser_identities = configured_identities
        await get_or_create_user(
            session,
            identity=admin_identity,
            role=admin_role,
        )
        hairdressers = [
            await get_or_create_user(
                session,
                identity=identity,
                role=hairdresser_role,
            )
            for identity in hairdresser_identities
        ]
        services = [
            await get_or_create_service(session, definition=definition)
            for definition in INITIAL_SERVICES
        ]

        for hairdresser in hairdressers:
            await ensure_weekly_availability(
                session,
                hairdresser=hairdresser,
                schedule=BASE_WEEKLY_SCHEDULE,
            )
            for service in services:
                await ensure_capability(session, user=hairdresser, service=service)

        # Deactivate any legacy placeholder users that are not part of the active
        # seed plan
        active_seed_emails = {identity.email for identity in configured_identities}
        legacy_users = (
            await session.scalars(
                select(User).where(
                    User.email_google.like("%@afterlook.com"),
                    User.email_google.not_in(active_seed_emails),
                )
            )
        ).all()
        for legacy_user in legacy_users:
            legacy_user.activo = False


if __name__ == "__main__":
    asyncio.run(seed())
