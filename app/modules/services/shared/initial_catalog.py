"""Versioned initial service catalog used only by the development seed."""

from dataclasses import dataclass

from app.modules.services.shared.service_types import ServiceType


@dataclass(frozen=True, slots=True)
class InitialService:
    """Describe one service that must exist after the initial seed runs."""

    name: str
    service_type: ServiceType
    duration_minutes: int
    description: str | None = None


INITIAL_SERVICES: tuple[InitialService, ...] = (
    InitialService(
        name="Corte de cabello",
        service_type=ServiceType.PELUQUERIA,
        duration_minutes=60,
    ),
    InitialService(
        name="Barbería",
        service_type=ServiceType.BARBERIA,
        duration_minutes=60,
    ),
)
