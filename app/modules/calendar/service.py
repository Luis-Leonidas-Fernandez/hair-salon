"""Domain service for calendar feed retrieval and aggregation (ADR-018, CU-012)."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.calendar.ics_builder import build_hairdresser_ics_feed
from app.modules.services.shared.domain_types import BookingStatus
from app.modules.services.shared.models import Booking, User


async def get_hairdresser_calendar_feed(
    db: AsyncSession,
    hairdresser_id: int,
    salon_name: str,
    salon_address: str,
    days_back: int = 7,
    days_forward: int = 60,
) -> str:
    """Obtiene reservas del peluquero y genera el texto iCalendar."""
    # 1. Obtener datos del peluquero
    hairdresser = await db.get(User, hairdresser_id)
    if not hairdresser or not hairdresser.activo:
        raise ValueError("HAIRDRESSER_NOT_FOUND_OR_INACTIVE")

    # 2. Filtrar reservas en ventana temporal relevante
    now = datetime.now(UTC)
    since = now - timedelta(days=days_back)
    until = now + timedelta(days=days_forward)

    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.cliente),
            selectinload(Booking.servicio),
        )
        .where(
            Booking.peluquero_id == hairdresser_id,
            Booking.fecha_inicio >= since,
            Booking.fecha_inicio <= until,
            Booking.estado.in_(
                [
                    BookingStatus.CONFIRMED.value,
                    BookingStatus.PENDING.value,
                    BookingStatus.CANCELLED.value,
                ]
            ),
        )
        .order_by(Booking.fecha_inicio.asc())
    )

    result = await db.execute(stmt)
    bookings = list(result.scalars().all())

    return build_hairdresser_ics_feed(
        hairdresser=hairdresser,
        bookings=bookings,
        salon_name=salon_name,
        salon_address=salon_address,
    )
