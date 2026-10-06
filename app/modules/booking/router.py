"""HTTP controller for salon booking API (CU-003).

Adheres to SRP: Handles HTTP request validation, session authentication,
delegating queries and commands to booking domain service.
"""

from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.infrastructure.database.session import get_db_session
from app.modules.booking.schemas import (
    AvailabilityResponse,
    BookingResponse,
    CreateBookingRequest,
    HairdresserBookingClient,
    HairdresserBookingResponse,
    HairdresserResponse,
    ServiceResponse,
    UpdateBookingStatusRequest,
)
from app.modules.booking.service import (
    create_booking,
    get_active_hairdressers,
    get_active_services,
    get_client_bookings,
    get_hairdresser_availability,
    get_hairdresser_bookings,
    update_booking_status_by_hairdresser,
)
from app.modules.identity.session import extract_session

router = APIRouter(prefix="/api/booking", tags=["Booking"])


@router.get("/services", response_model=list[ServiceResponse])
async def list_services(
    db: AsyncSession = Depends(get_db_session),
) -> list[ServiceResponse]:
    """Retrieve all active salon services."""
    services = await get_active_services(db)
    return [ServiceResponse.model_validate(s) for s in services]


@router.get("/hairdressers", response_model=list[HairdresserResponse])
async def list_hairdressers(
    db: AsyncSession = Depends(get_db_session),
) -> list[HairdresserResponse]:
    """Retrieve all active stylists (peluqueros)."""
    hairdressers = await get_active_hairdressers(db)
    return [HairdresserResponse.model_validate(h) for h in hairdressers]


@router.get("/availability", response_model=AvailabilityResponse)
async def check_availability(
    peluquero_id: int = Query(..., description="ID del peluquero"),
    fecha: date = Query(..., description="Fecha deseada YYYY-MM-DD"),
    duracion_minutos: int = Query(60, description="Duración en minutos"),
    db: AsyncSession = Depends(get_db_session),
) -> AvailabilityResponse:
    """Return available 30-min start time slots for stylist on given date."""
    slots = await get_hairdresser_availability(
        db,
        peluquero_id=peluquero_id,
        fecha=fecha,
        duracion_minutos=duracion_minutos,
    )
    return AvailabilityResponse(
        fecha=fecha,
        peluquero_id=peluquero_id,
        slots=slots,
    )


@router.post(
    "/reserve", response_model=BookingResponse, status_code=status.HTTP_201_CREATED
)
async def reserve_appointment(
    payload: CreateBookingRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> BookingResponse:
    """Create a new appointment for the currently authenticated client (CU-003)."""
    session = extract_session(
        request,
        settings.secret_key,
        settings.session_cookie_name,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED",
        )

    if session.actor_type != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SOLO_CLIENTES_PUEDEN_RESERVAR",
        )

    booking = await create_booking(db, client_id=session.sub, request=payload)

    return BookingResponse(
        id=booking.id,
        cliente_id=booking.cliente_id,
        servicio_id=booking.servicio_id,
        servicio_nombre=booking.servicio.nombre if booking.servicio else "Servicio",
        peluquero_id=booking.peluquero_id,
        peluquero_nombre=booking.peluquero.nombre_completo
        if booking.peluquero
        else "Peluquero",
        fecha_inicio=booking.fecha_inicio,
        duracion_minutos=booking.duracion_minutos,
        estado=booking.estado,
        canal_reserva=booking.canal_reserva,
        notas_cliente=booking.notas_cliente,
        created_at=booking.created_at,
    )


@router.get("/my", response_model=list[BookingResponse])
async def list_my_bookings(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> list[BookingResponse]:
    """Retrieve past and active bookings for currently logged-in client."""
    session = extract_session(
        request,
        settings.secret_key,
        settings.session_cookie_name,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED",
        )

    if session.actor_type != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SOLO_CLIENTES",
        )

    bookings = await get_client_bookings(db, client_id=session.sub)
    return [
        BookingResponse(
            id=b.id,
            cliente_id=b.cliente_id,
            servicio_id=b.servicio_id,
            servicio_nombre=b.servicio.nombre if b.servicio else "Servicio",
            peluquero_id=b.peluquero_id,
            peluquero_nombre=b.peluquero.nombre_completo
            if b.peluquero
            else "Peluquero",
            fecha_inicio=b.fecha_inicio,
            duracion_minutos=b.duracion_minutos,
            estado=b.estado,
            canal_reserva=b.canal_reserva,
            notas_cliente=b.notas_cliente,
            created_at=b.created_at,
        )
        for b in bookings
    ]


def _to_hairdresser_booking_response(b) -> HairdresserBookingResponse:
    fecha_fin = b.fecha_fin
    if fecha_fin is None:
        fecha_fin = b.fecha_inicio + timedelta(minutes=b.duracion_minutos)

    return HairdresserBookingResponse(
        id=b.id,
        cliente=HairdresserBookingClient(
            id=b.cliente.id if b.cliente else b.cliente_id,
            nombre=b.cliente.nombre if b.cliente else "Cliente",
            telefono=b.cliente.telefono if b.cliente else None,
            whatsapp=b.cliente.whatsapp if b.cliente else None,
            email=b.cliente.email_google if b.cliente else "",
        ),
        servicio_id=b.servicio_id,
        servicio_nombre=b.servicio.nombre if b.servicio else "Servicio",
        tipo_servicio=b.servicio.tipo_servicio if b.servicio else "GENERAL",
        duracion_minutos=b.duracion_minutos,
        precio_estimado=b.precio_estimado
        if b.precio_estimado is not None
        else Decimal("0.00"),
        fecha_inicio=b.fecha_inicio,
        fecha_fin=fecha_fin,
        estado=b.estado,
        canal_reserva=b.canal_reserva,
        notas_cliente=b.notas_cliente,
        created_at=b.created_at if b.created_at is not None else b.fecha_inicio,
    )


@router.get("/hairdresser/my", response_model=list[HairdresserBookingResponse])
async def list_hairdresser_my_bookings(
    request: Request,
    fecha: date | None = Query(None, description="Filtrar por fecha YYYY-MM-DD"),
    estado: str | None = Query(None, description="Filtrar por estado"),
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> list[HairdresserBookingResponse]:
    """Retrieve reservations assigned to currently logged-in hairdresser (CU-010)."""
    session = extract_session(
        request,
        settings.secret_key,
        settings.session_cookie_name,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED",
        )

    if session.actor_type != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN_CLIENT_ACTOR",
        )

    bookings = await get_hairdresser_bookings(
        db,
        hairdresser_id=session.sub,
        fecha=fecha,
        estado=estado,
    )
    return [_to_hairdresser_booking_response(b) for b in bookings]


@router.patch(
    "/hairdresser/bookings/{booking_id}/status",
    response_model=HairdresserBookingResponse,
)
async def update_booking_status(
    booking_id: int,
    payload: UpdateBookingStatusRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> HairdresserBookingResponse:
    """Transition appointment status by the hairdresser (CU-011)."""
    session = extract_session(
        request,
        settings.secret_key,
        settings.session_cookie_name,
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NOT_AUTHENTICATED",
        )

    if session.actor_type != "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN_CLIENT_ACTOR",
        )

    updated_booking = await update_booking_status_by_hairdresser(
        db,
        hairdresser_id=session.sub,
        booking_id=booking_id,
        nuevo_estado=payload.estado,
        motivo=payload.motivo,
    )
    return _to_hairdresser_booking_response(updated_booking)
