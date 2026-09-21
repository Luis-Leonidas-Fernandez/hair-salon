"""Validate seed inputs and existing records before the seed mutates data."""

from collections import Counter
from collections.abc import Sequence
from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.services.shared.errors import SeedValidationError
from app.modules.services.shared.initial_catalog import InitialService
from app.modules.services.shared.initial_roles import InitialRole
from app.modules.services.shared.models import (
    Availability,
    Role,
    Service,
    User,
    UserService,
)
from app.modules.services.shared.seed_plan import (
    EXPECTED_SEED_ROLE_COUNTS,
    SeedIdentity,
)


def validate_seed_configuration(
    *,
    identities: Sequence[SeedIdentity],
    initial_roles: Sequence[InitialRole],
    initial_services: Sequence[InitialService],
) -> None:
    """Reject incomplete, duplicated, or structurally invalid seed definitions."""

    _validate_seed_identities(identities)
    _validate_initial_roles(initial_roles)
    _validate_initial_services(initial_services)


def validate_existing_role(*, role: Role | None, definition: InitialRole) -> None:
    """Reject an inactive role that would make the seeded staff unusable."""

    if role is not None and not role.activo:
        raise SeedValidationError(
            f"Initial role {definition.name.value!r} already exists but is inactive."
        )


def validate_existing_user_role(
    *, user: User | None, identity: SeedIdentity, role_id: int
) -> None:
    """Reject an existing account that conflicts with seed configuration."""

    if user is None:
        return
    if not user.activo:
        raise SeedValidationError(
            f"Seed user {identity.email!r} already exists but is inactive."
        )
    if user.rol_id != role_id:
        raise SeedValidationError(
            "Seed email "
            f"{identity.email!r} already belongs to a user with a different role."
        )


def validate_existing_service(
    *, service: Service | None, definition: InitialService
) -> None:
    """Reject a name collision whose immutable service attributes differ."""

    if service is None:
        return
    if not service.activo:
        raise SeedValidationError(
            f"Service {definition.name!r} already exists but is inactive."
        )

    expected_type = definition.service_type.value
    if (
        service.tipo_servicio != expected_type
        or service.duracion_minutos != definition.duration_minutes
    ):
        raise SeedValidationError(
            "Service "
            f"{definition.name!r} already exists with a different type or duration."
        )


def validate_existing_capability(*, capability: UserService | None) -> None:
    """Reject an inactive staff-service relation instead of reactivating it."""

    if capability is not None and not capability.activo:
        raise SeedValidationError(
            "A seeded staff-service capability already exists but is inactive."
        )


async def validate_weekly_availability(
    session: AsyncSession,
    *,
    hairdresser: User,
    weekday: int,
    start_time: time,
    end_time: time,
) -> bool:
    """Return whether the exact schedule exists or reject a conflicting schedule."""

    existing_availabilities = list(
        (
            await session.scalars(
                select(Availability).where(
                    Availability.usuario_id == hairdresser.id,
                    Availability.dia_semana == weekday,
                    Availability.bloqueo_excepcional.is_(False),
                )
            )
        ).all()
    )

    exact_schedule_exists = False
    for availability in existing_availabilities:
        if not availability.activa:
            raise SeedValidationError(
                "An existing weekly availability is inactive for "
                f"{hairdresser.email_google!r} on weekday {weekday}."
            )
        if (
            availability.hora_desde == start_time
            and availability.hora_hasta == end_time
        ):
            exact_schedule_exists = True
            continue
        raise SeedValidationError(
            "An existing weekly availability differs from the seed schedule for "
            f"{hairdresser.email_google!r} on weekday {weekday}."
        )

    return exact_schedule_exists


def _validate_seed_identities(identities: Sequence[SeedIdentity]) -> None:
    expected_identity_count = sum(EXPECTED_SEED_ROLE_COUNTS.values())
    if len(identities) != expected_identity_count:
        raise SeedValidationError(
            "The seed identity count does not match the initial staff plan."
        )

    normalized_emails: set[str] = set()
    for identity in identities:
        if not identity.display_name:
            raise SeedValidationError("Seed user names cannot be empty.")
        if not _looks_like_email(identity.email):
            raise SeedValidationError(f"Seed email {identity.email!r} is not valid.")
        if identity.email in normalized_emails:
            raise SeedValidationError("Seed user emails must be distinct.")
        normalized_emails.add(identity.email)

    actual_role_counts = Counter(identity.expected_role for identity in identities)
    if actual_role_counts != EXPECTED_SEED_ROLE_COUNTS:
        raise SeedValidationError(
            "Seed identities do not match the configured initial role plan."
        )


def _validate_initial_roles(initial_roles: Sequence[InitialRole]) -> None:
    role_names = [role.name for role in initial_roles]
    if len(role_names) != len(set(role_names)):
        raise SeedValidationError("Initial roles cannot contain duplicates.")
    if set(role_names) != set(EXPECTED_SEED_ROLE_COUNTS):
        raise SeedValidationError(
            "Initial roles do not match the configured initial role plan."
        )
    if any(not role.description.strip() for role in initial_roles):
        raise SeedValidationError("Initial role descriptions cannot be empty.")


def _validate_initial_services(initial_services: Sequence[InitialService]) -> None:
    normalized_names: set[str] = set()
    for service in initial_services:
        normalized_name = service.name.strip().casefold()
        if not normalized_name:
            raise SeedValidationError("Initial service names cannot be empty.")
        if normalized_name in normalized_names:
            raise SeedValidationError("Initial service names must be unique.")
        if service.duration_minutes <= 0:
            raise SeedValidationError(
                "Initial service duration must be greater than zero."
            )
        normalized_names.add(normalized_name)


def _looks_like_email(value: str) -> bool:
    """Perform a lightweight configuration check before Google verifies identities."""

    local_part, separator, domain = value.partition("@")
    return bool(
        separator and local_part and domain and "." in domain and " " not in value
    )
