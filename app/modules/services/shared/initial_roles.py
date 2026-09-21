"""Versioned initial internal-role catalog used only by the development seed."""

from dataclasses import dataclass

from app.modules.services.shared.role_types import InternalRole


@dataclass(frozen=True, slots=True)
class InitialRole:
    """Describe one internal role that must exist after the initial seed runs."""

    name: InternalRole
    description: str


INITIAL_ROLES: tuple[InitialRole, ...] = (
    InitialRole(
        name=InternalRole.ADMIN,
        description="Administración general del sistema",
    ),
    InitialRole(
        name=InternalRole.PELUQUERO,
        description="Gestión de agenda y atención",
    ),
)
