"""Domain service for booking management and schedule evaluation (CU-003).

Adheres to SRP: Encapsulates catalog retrieval, slot availability calculation,
conflict resolution, and booking persistence with audit history.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.booking.schemas import CreateBookingRequest, TimeSlot
from app.modules.services.shared.domain_types import (
    BookingChannel,
    BookingStatus,
    ClientAccountStatus,
)
from app.modules.services.shared.models import (
    Availability,
    Booking,
    BookingHistory,
    Client,
    Service,
    User,
)
from app.shared.errors.business_rule_error import BusinessRuleError
from app.shared.errors.conflict_error import ConflictError
from app.shared.errors.not_found_error import NotFoundError

TZ_AR = ZoneInfo("America/Argentina/Buenos_Aires")


async def get_active_services(session: AsyncSession) -> list[Service]:
    """Return all active services offered by the salon."""
    stmt = select(Service).where(Service.activo.is_(True)).order_by(Service.id)
    result = await session.scalars(stmt)
    return list(result.all())


async def get_active_hairdressers(session: AsyncSession) -> list[User]:
    """Return all active stylists with the PELUQUERO role."""
    stmt = (
        select(User)
        .options(selectinload(User.rol))
        .where(User.activo.is_(True))
        .order_by(User.id)
    )
    result = await session.scalars(stmt)
    hairdressers = [u for u in result.all() if u.rol and u.rol.nombre == "PELUQUERO"]
    return hairdressers


async def get_hairdresser_availability(
    session: AsyncSession,
    *,
    peluquero_id: int,
    fecha: date,
    duracion_minutos: int = 60,
) -> list[TimeSlot]:
    """Compute available 30-minute booking start slots for a stylist on a given date."""
    # 1. Check stylist base weekly availability (1 = Monday ... 7 = Sunday)
    weekday = fecha.isoweekday()
    if weekday == 7:  # Sunday is closed
        return []

    avail_stmt = select(Availability).where(
        Availability.usuario_id == peluquero_id,
        Availability.dia_semana == weekday,
        Availability.activa.is_(True),
        Availability.bloqueo_excepcional.is_(False),
    )
    availability = await session.scalar(avail_stmt)
    if availability is None:
        return []

    hora_desde = availability.hora_desde
    hora_hasta = availability.hora_hasta

    # 2. Query active existing bookings overlapping with this date
    # Active states that occupy schedule
    active_occupying_statuses = {
        BookingStatus.PENDING.value,
        BookingStatus.SCHEDULED.value,
        BookingStatus.RESERVED.value,
        BookingStatus.CONFIRMED.value,
    }

    # Query bookings for this hairdresser starting around this date
    # In local time window
    day_start_local = datetime(fecha.year, fecha.month, fecha.day, 0, 0, tzinfo=TZ_AR)
    day_end_local = day_start_local + timedelta(days=1)

    bookings_stmt = select(Booking).where(
        Booking.peluquero_id == peluquero_id,
        Booking.estado.in_(active_occupying_statuses),
        Booking.fecha_inicio >= day_start_local - timedelta(hours=2),
        Booking.fecha_inicio <= day_end_local + timedelta(hours=2),
    )
    existing_bookings = list((await session.scalars(bookings_stmt)).all())

    # 3. Generate candidate 30-minute start slots
    now_local = datetime.now(TZ_AR)
    current_time_minutes = hora_desde.hour * 60 + hora_desde.minute
    end_time_minutes = hora_hasta.hour * 60 + hora_hasta.minute

    slots: list[TimeSlot] = []

    while current_time_minutes + duracion_minutos <= end_time_minutes:
        h = current_time_minutes // 60
        m = current_time_minutes % 60
        slot_label = f"{h:02d}:{m:02d}"

        slot_start_dt = datetime(fecha.year, fecha.month, fecha.day, h, m, tzinfo=TZ_AR)
        slot_end_dt = slot_start_dt + timedelta(minutes=duracion_minutos)

        # Check if slot is in the past
        is_past = fecha == now_local.date() and slot_start_dt <= now_local

        # Check overlap with existing bookings
        overlaps = False
        for b in existing_bookings:
            b_start = b.fecha_inicio.astimezone(TZ_AR)
            b_end = b_start + timedelta(minutes=b.duracion_minutos)
            # Overlap condition: slot_start < b_end AND slot_end > b_start
            if slot_start_dt < b_end and slot_end_dt > b_start:
                overlaps = True
                break

        slots.append(
            TimeSlot(
                hora=slot_label,
                disponible=not (is_past or overlaps),
            )
        )

        current_time_minutes += 30

    return slots


async def create_booking(
    session: AsyncSession,
    *,
    client_id: int,
    request: CreateBookingRequest,
) -> Booking:
    """Create a validated salon reservation with initial history."""
    # 1. Validate Client
    client_stmt = select(Client).where(Client.id == client_id)
    client = await session.scalar(client_stmt)
    if client is None:
        raise NotFoundError(code="CLIENT_NOT_FOUND", message="Cliente no encontrado.")

    if client.estado_cuenta != ClientAccountStatus.ACTIVE.value:
        raise BusinessRuleError(
            code="CLIENT_ACCOUNT_SUSPENDED",
            message="Tu cuenta se encuentra suspendida o inactiva.",
        )

    if not (client.telefono or client.whatsapp):
        raise BusinessRuleError(
            code="PROFILE_INCOMPLETE",
            message=(
                "Debes completar tus datos de contacto (teléfono) antes de reservar."
            ),
        )

    # 2. Validate Service
    service_stmt = select(Service).where(Service.id == request.servicio_id)
    service = await session.scalar(service_stmt)
    if service is None or not service.activo:
        raise NotFoundError(
            code="SERVICE_NOT_FOUND",
            message="El servicio seleccionado no está disponible.",
        )

    # 3. Validate Hairdresser
    user_stmt = (
        select(User)
        .options(selectinload(User.rol))
        .where(User.id == request.peluquero_id)
    )
    hairdresser = await session.scalar(user_stmt)
    if (
        hairdresser is None
        or not hairdresser.activo
        or not hairdresser.rol
        or hairdresser.rol.nombre != "PELUQUERO"
    ):
        raise NotFoundError(
            code="HAIRDRESSER_NOT_FOUND",
            message="El profesional seleccionado no está disponible.",
        )

    # 4. Validate Date window (today to today + 31 days)
    now_local = datetime.now(TZ_AR)
    today = now_local.date()
    max_date = today + timedelta(days=31)

    if request.fecha < today:
        raise BusinessRuleError(
            code="INVALID_DATE_PAST",
            message="No se pueden solicitar turnos en fechas pasadas.",
        )
    if request.fecha > max_date:
        raise BusinessRuleError(
            code="INVALID_DATE_EXCEEDS_WINDOW",
            message="No se pueden solicitar turnos con más de un mes de anticipación.",
        )

    # 5. Parse and validate slot availability
    hours, minutes = map(int, request.hora.split(":"))
    slot_start_dt = datetime(
        request.fecha.year,
        request.fecha.month,
        request.fecha.day,
        hours,
        minutes,
        tzinfo=TZ_AR,
    )

    if slot_start_dt <= now_local:
        raise BusinessRuleError(
            code="INVALID_TIME_PAST",
            message="El horario solicitado ya ha transcurrido.",
        )

    # Check availability calculation
    available_slots = await get_hairdresser_availability(
        session,
        peluquero_id=hairdresser.id,
        fecha=request.fecha,
        duracion_minutos=service.duracion_minutos,
    )

    chosen_slot = next((s for s in available_slots if s.hora == request.hora), None)
    if chosen_slot is None or not chosen_slot.disponible:
        raise ConflictError(
            code="SLOT_NOT_AVAILABLE",
            message=(
                "El horario seleccionado ya no se encuentra disponible. "
                "Por favor elegí otro."
            ),
        )

    # 6. Instantiate Booking
    booking = Booking(
        cliente_id=client.id,
        peluquero_id=hairdresser.id,
        servicio_id=service.id,
        fecha_inicio=slot_start_dt,
        duracion_minutos=service.duracion_minutos,
        estado=BookingStatus.CONFIRMED.value,
        canal_reserva=BookingChannel.WEB.value,
        precio_estimado=service.precio_base or Decimal("0.00"),
        notas_cliente=request.notas_cliente,
    )
    session.add(booking)

    # 7. Add initial history entry (CU-003 step 8)
    history = BookingHistory(
        reserva=booking,
        estado_anterior=None,
        estado_nuevo=BookingStatus.CONFIRMED.value,
        motivo="Reserva creada desde la plataforma web",
        realizado_por_usuario_id=None,
    )
    session.add(history)

    try:
        await session.commit()
        await session.refresh(booking, ["servicio", "peluquero", "cliente"])
    except IntegrityError as err:
        await session.rollback()
        raise ConflictError(
            code="SLOT_CONFLICT",
            message=(
                "El turno seleccionado fue reservado por otro usuario en este instante."
            ),
        ) from err

    return booking


async def get_client_bookings(
    session: AsyncSession, *, client_id: int
) -> list[Booking]:
    """Retrieve all reservations for a specific client ordered chronologically."""
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.servicio),
            selectinload(Booking.peluquero),
        )
        .where(Booking.cliente_id == client_id)
        .order_by(Booking.fecha_inicio.desc())
    )
    result = await session.scalars(stmt)
    return list(result.all())


async def get_hairdresser_bookings(
    session: AsyncSession,
    hairdresser_id: int,
    fecha: date | None = None,
    estado: str | None = None,
) -> list[Booking]:
    """Retrieve reservations assigned to a hairdresser with optional
    date and status filters (CU-010).
    """
    stmt = (
        select(Booking)
        .options(
            joinedload(Booking.cliente),
            joinedload(Booking.servicio),
        )
        .where(Booking.peluquero_id == hairdresser_id)
    )
    if fecha is not None:
        stmt = stmt.where(func.date(Booking.fecha_inicio) == fecha)
    if estado is not None:
        stmt = stmt.where(Booking.estado == estado)
    stmt = stmt.order_by(Booking.fecha_inicio.asc())

    result = await session.scalars(stmt)
    return list(result.unique().all())


async def update_booking_status_by_hairdresser(
    session: AsyncSession,
    hairdresser_id: int,
    booking_id: int,
    nuevo_estado: str,
    motivo: str | None = None,
) -> Booking:
    """Transition booking status with audit history initiated by the
    assigned hairdresser (CU-011).
    """
    stmt = (
        select(Booking)
        .options(
            joinedload(Booking.cliente),
            joinedload(Booking.servicio),
        )
        .where(Booking.id == booking_id)
    )
    result = await session.scalars(stmt)
    booking = result.unique().first()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BOOKING_NOT_FOUND",
        )

    if booking.peluquero_id != hairdresser_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="NOT_YOUR_BOOKING",
        )

    valid_statuses = [s.value for s in BookingStatus]
    if nuevo_estado not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_STATUS",
        )

    estado_anterior = booking.estado
    booking.estado = nuevo_estado

    history = BookingHistory(
        reserva_id=booking.id,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        motivo=motivo or f"Cambio de estado a {nuevo_estado} por el peluquero",
        realizado_por_usuario_id=hairdresser_id,
    )
    session.add(history)

    await session.commit()
    await session.refresh(booking, ["cliente", "servicio"])

    return booking
