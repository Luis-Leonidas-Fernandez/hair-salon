"""Unit tests for the controlled domain vocabularies."""

from app.modules.services.shared.domain_types import (
    BookingChannel,
    BookingStatus,
    CalendarProvider,
    CalendarSyncStatus,
    ClientAccountStatus,
    NotificationChannel,
    NotificationStatus,
)
from app.modules.services.shared.role_types import InternalRole
from app.modules.services.shared.service_types import ServiceType


def test_domain_vocabularies_expose_database_values() -> None:
    """Enums must preserve the values already used by the database schema."""

    assert ClientAccountStatus.ACTIVE.value == "ACTIVA"
    assert BookingStatus.CONFIRMED.value == "CONFIRMADA"
    assert BookingChannel.PHONE.value == "TELEFONO"
    assert NotificationChannel.WHATSAPP.value == "WHATSAPP"
    assert NotificationStatus.SENT.value == "ENVIADA"
    assert CalendarProvider.GOOGLE_CALENDAR.value == "GOOGLE_CALENDAR"
    assert CalendarSyncStatus.SYNCHRONIZED.value == "SINCRONIZADO"


def test_existing_role_and_service_vocabularies_remain_stable() -> None:
    """Existing seed vocabularies remain compatible with the refactor."""

    assert InternalRole.CLIENTE.value == "CLIENTE"
    assert ServiceType.PELUQUERIA.value == "PELUQUERIA"
