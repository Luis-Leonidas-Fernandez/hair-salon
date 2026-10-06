"""Typed plan for the initial staff and schedule loaded by the seed."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import TYPE_CHECKING

from app.modules.services.shared.role_types import InternalRole

if TYPE_CHECKING:
    from app.config.settings import Settings


@dataclass(frozen=True, slots=True)
class SeedIdentity:
    """Represent one internal identity configured for the initial seed."""

    display_name: str
    email: str
    expected_role: InternalRole

    def __post_init__(self) -> None:
        """Store canonical values for validation and persistence."""

        object.__setattr__(self, "display_name", self.display_name.strip())
        object.__setattr__(self, "email", self.email.strip().casefold())


@dataclass(frozen=True, slots=True)
class WeeklySchedule:
    """Describe one weekly availability pattern shared by the initial staff."""

    weekdays: tuple[int, ...]
    start_time: time
    end_time: time


BASE_WEEKLY_SCHEDULE = WeeklySchedule(
    weekdays=(1, 2, 3, 4, 5, 6),
    start_time=time(9, 30),
    end_time=time(22, 0),
)

EXPECTED_SEED_ROLE_COUNTS: dict[InternalRole, int] = {
    InternalRole.ADMIN: 1,
    InternalRole.PELUQUERO: 3,
}


def build_seed_identities(settings: Settings) -> tuple[SeedIdentity, ...]:
    """Map environment configuration to the initial staff plan."""

    return (
        SeedIdentity(
            display_name=settings.seed_admin_name,
            email=settings.seed_admin_email,
            expected_role=InternalRole.ADMIN,
        ),
        SeedIdentity(
            display_name=settings.seed_hairdresser_1_name,
            email=settings.seed_hairdresser_1_email,
            expected_role=InternalRole.PELUQUERO,
        ),
        SeedIdentity(
            display_name=settings.seed_hairdresser_2_name,
            email=settings.seed_hairdresser_2_email,
            expected_role=InternalRole.PELUQUERO,
        ),
        SeedIdentity(
            display_name=settings.seed_hairdresser_3_name,
            email=settings.seed_hairdresser_3_email,
            expected_role=InternalRole.PELUQUERO,
        ),
    )
