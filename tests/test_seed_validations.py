"""Unit tests for the safety rules applied by the initial data seed."""

import asyncio
from datetime import time

import pytest

from app.modules.services.shared.errors import SeedValidationError
from app.modules.services.shared.initial_catalog import INITIAL_SERVICES, InitialService
from app.modules.services.shared.initial_roles import INITIAL_ROLES
from app.modules.services.shared.models import (
    Availability,
    Role,
    Service,
    User,
    UserService,
)
from app.modules.services.shared.role_types import InternalRole
from app.modules.services.shared.seed_plan import SeedIdentity
from app.modules.services.shared.seed_validations import (
    validate_existing_capability,
    validate_existing_role,
    validate_existing_service,
    validate_existing_user_role,
    validate_seed_configuration,
    validate_weekly_availability,
)
from app.modules.services.shared.service_types import ServiceType


class FakeScalarResult:
    """Expose the minimal SQLAlchemy scalar-result API required by one test."""

    def __init__(self, values: list[Availability]) -> None:
        self._values = values

    def all(self) -> list[Availability]:
        """Return the availability records configured for the fake query."""

        return self._values


class FakeAvailabilitySession:
    """Return predefined availability records without requiring a test database."""

    def __init__(self, availabilities: list[Availability]) -> None:
        self._availabilities = availabilities

    async def scalars(self, _statement: object) -> FakeScalarResult:
        """Return records as if the schedule query had been executed."""

        return FakeScalarResult(self._availabilities)


@pytest.fixture
def valid_identities() -> tuple[SeedIdentity, ...]:
    """Return distinct internal identities accepted by the seed validator."""

    return (
        SeedIdentity("Admin", "admin@example.com", InternalRole.ADMIN),
        SeedIdentity("Hairdresser One", "one@example.com", InternalRole.PELUQUERO),
        SeedIdentity("Hairdresser Two", "two@example.com", InternalRole.PELUQUERO),
    )


# Configuration validation ----------------------------------------------------


def test_accepts_valid_seed_configuration(
    valid_identities: tuple[SeedIdentity, ...],
) -> None:
    """A complete catalog and distinct identities pass validation."""

    validate_seed_configuration(
        identities=valid_identities,
        initial_roles=INITIAL_ROLES,
        initial_services=INITIAL_SERVICES,
    )


def test_rejects_duplicate_seed_emails(
    valid_identities: tuple[SeedIdentity, ...],
) -> None:
    """Duplicated emails fail before the seed opens its database transaction."""

    duplicated_identities = (
        valid_identities[0],
        SeedIdentity("Hairdresser One", "ADMIN@example.com", InternalRole.PELUQUERO),
        valid_identities[2],
    )

    with pytest.raises(SeedValidationError, match="emails must be distinct"):
        validate_seed_configuration(
            identities=duplicated_identities,
            initial_roles=INITIAL_ROLES,
            initial_services=INITIAL_SERVICES,
        )


def test_rejects_non_positive_service_duration(
    valid_identities: tuple[SeedIdentity, ...],
) -> None:
    """A service with an invalid duration is rejected before persistence."""

    invalid_services = (
        InitialService(
            name="Invalid service",
            service_type=ServiceType.PELUQUERIA,
            duration_minutes=0,
        ),
    )

    with pytest.raises(SeedValidationError, match="duration"):
        validate_seed_configuration(
            identities=valid_identities,
            initial_roles=INITIAL_ROLES,
            initial_services=invalid_services,
        )


def test_normalizes_seed_identity_before_validation() -> None:
    """Whitespace and email casing are removed before persistence."""

    identity = SeedIdentity("  Admin  ", " ADMIN@EXAMPLE.COM ", InternalRole.ADMIN)

    assert identity.display_name == "Admin"
    assert identity.email == "admin@example.com"


# Existing database records ---------------------------------------------------


def test_rejects_existing_user_with_a_different_role() -> None:
    """An email already assigned to another role cannot be reused by the seed."""

    existing_admin = User(
        nombre_completo="Existing Admin",
        email_google="shared@example.com",
        rol_id=1,
        activo=True,
    )
    hairdresser_identity = SeedIdentity(
        "Hairdresser One", "shared@example.com", InternalRole.PELUQUERO
    )

    with pytest.raises(SeedValidationError, match="different role"):
        validate_existing_user_role(
            user=existing_admin,
            identity=hairdresser_identity,
            role_id=2,
        )


def test_rejects_existing_service_with_a_different_duration() -> None:
    """A catalog name collision with another duration fails safely."""

    existing_service = Service(
        nombre="Corte de cabello",
        tipo_servicio=ServiceType.PELUQUERIA.value,
        duracion_minutos=30,
        activo=True,
    )
    expected_service = InitialService(
        name="Corte de cabello",
        service_type=ServiceType.PELUQUERIA,
        duration_minutes=60,
    )

    with pytest.raises(SeedValidationError, match="different type or duration"):
        validate_existing_service(
            service=existing_service,
            definition=expected_service,
        )


def test_rejects_inactive_existing_records() -> None:
    """Inactive roles, users, services, and capabilities require human review."""

    inactive_role = Role(nombre=InternalRole.ADMIN.value, activo=False)
    inactive_user = User(
        nombre_completo="Inactive Admin",
        email_google="admin@example.com",
        rol_id=1,
        activo=False,
    )
    inactive_service = Service(
        nombre="Barbería",
        tipo_servicio=ServiceType.BARBERIA.value,
        duracion_minutos=60,
        activo=False,
    )
    inactive_capability = UserService(usuario_id=1, servicio_id=1, activo=False)
    admin_identity = SeedIdentity("Admin", "admin@example.com", InternalRole.ADMIN)

    with pytest.raises(SeedValidationError, match="inactive"):
        validate_existing_role(role=inactive_role, definition=INITIAL_ROLES[0])
    with pytest.raises(SeedValidationError, match="inactive"):
        validate_existing_user_role(
            user=inactive_user,
            identity=admin_identity,
            role_id=1,
        )
    with pytest.raises(SeedValidationError, match="inactive"):
        validate_existing_service(
            service=inactive_service, definition=INITIAL_SERVICES[1]
        )
    with pytest.raises(SeedValidationError, match="inactive"):
        validate_existing_capability(capability=inactive_capability)


# Weekly availability ---------------------------------------------------------


def test_rejects_existing_weekly_schedule_that_differs_from_the_seed() -> None:
    """A manually configured weekly schedule is never mixed with the base schedule."""

    hairdresser = User(
        id=7,
        nombre_completo="Hairdresser One",
        email_google="one@example.com",
        rol_id=2,
        activo=True,
    )
    different_schedule = Availability(
        usuario_id=7,
        dia_semana=1,
        hora_desde=time(10, 0),
        hora_hasta=time(18, 0),
        bloqueo_excepcional=False,
        activa=True,
    )
    session = FakeAvailabilitySession([different_schedule])

    with pytest.raises(SeedValidationError, match="differs from the seed schedule"):
        asyncio.run(
            validate_weekly_availability(
                session,  # type: ignore[arg-type]
                hairdresser=hairdresser,
                weekday=1,
                start_time=time(9, 30),
                end_time=time(22, 0),
            )
        )


def test_rejects_inactive_weekly_schedule() -> None:
    """Inactive availability is not silently replaced by another base schedule."""

    hairdresser = User(
        id=7,
        nombre_completo="Hairdresser One",
        email_google="one@example.com",
        rol_id=2,
        activo=True,
    )
    inactive_schedule = Availability(
        usuario_id=7,
        dia_semana=1,
        hora_desde=time(9, 30),
        hora_hasta=time(22, 0),
        bloqueo_excepcional=False,
        activa=False,
    )
    session = FakeAvailabilitySession([inactive_schedule])

    with pytest.raises(SeedValidationError, match="is inactive"):
        asyncio.run(
            validate_weekly_availability(
                session,  # type: ignore[arg-type]
                hairdresser=hairdresser,
                weekday=1,
                start_time=time(9, 30),
                end_time=time(22, 0),
            )
        )
