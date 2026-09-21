"""Tests for database-level integrity metadata."""

from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import ExcludeConstraint

from app.modules.services.shared.models import Booking


def test_booking_has_generated_end_time() -> None:
    """Reservation end time must be derived from start time and duration."""

    fecha_fin = Booking.__table__.c.fecha_fin

    assert isinstance(fecha_fin.server_default, Computed)
    assert "duracion_minutos" in str(fecha_fin.server_default.sqltext)
    assert "UTC" in str(fecha_fin.server_default.sqltext)


def test_booking_has_active_overlap_exclusion_constraint() -> None:
    """PostgreSQL must reject overlapping active reservations per hairdresser."""

    exclusion_constraints = [
        constraint
        for constraint in Booking.__table__.constraints
        if isinstance(constraint, ExcludeConstraint)
    ]

    assert len(exclusion_constraints) == 1
    assert exclusion_constraints[0].name == "ex_reservas_peluquero_horario_activo"
    assert "CONFIRMADA" in str(exclusion_constraints[0].where)
