"""Tests for hairdresser appointments and reservations history (CU-010 & CU-011)."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
from fastapi import HTTPException, Response
from fastapi.testclient import TestClient

from app.config.settings import Settings, get_settings
from app.main import app
from app.modules.booking.service import update_booking_status_by_hairdresser
from app.modules.identity.session import issue_session_cookie
from app.modules.services.shared.domain_types import BookingChannel, BookingStatus
from app.modules.services.shared.models import (
    Booking,
    BookingHistory,
    Client,
    Service,
)

SECRET_KEY = "test-secret-key-at-least-32-bytes-long-1234"
TZ_AR = ZoneInfo("America/Argentina/Buenos_Aires")


def get_test_settings() -> Settings:
    return Settings(
        app_name="Test After Look",
        app_version="0.1.0",
        environment="development",
        database_url="postgresql+asyncpg://postgres:pass@localhost:5432/test",
        secret_key=SECRET_KEY,
        seed_admin_name="Admin",
        seed_admin_email="admin@example.com",
        seed_hairdresser_1_name="Hair1",
        seed_hairdresser_1_email="hair1@example.com",
        seed_hairdresser_2_name="Hair2",
        seed_hairdresser_2_email="hair2@example.com",
        seed_hairdresser_3_name="Hair3",
        seed_hairdresser_3_email="hair3@example.com",
        session_cookie_name="afterlook_session",
    )


def test_hairdresser_bookings_unauthenticated_returns_401() -> None:
    """GET /api/booking/hairdresser/my returns 401 without cookie."""
    client = TestClient(app)
    response = client.get("/api/booking/hairdresser/my")
    assert response.status_code == 401
    assert response.json()["detail"] == "NOT_AUTHENTICATED"


def test_hairdresser_bookings_client_returns_403() -> None:
    """GET /api/booking/hairdresser/my returns 403 for client actor."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    dummy_resp = Response()
    issue_session_cookie(
        dummy_resp,
        actor_id=1,
        actor_type="cliente",
        role="CLIENTE",
        email="cliente@example.com",
        nombre="Cliente Feliz",
        profile_complete=True,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
    )
    raw_cookie = dummy_resp.headers["set-cookie"].split(";")[0].split("=")[1]
    client.cookies.set(settings.session_cookie_name, raw_cookie)

    response = client.get("/api/booking/hairdresser/my")
    assert response.status_code == 403
    assert response.json()["detail"] == "FORBIDDEN_CLIENT_ACTOR"

    app.dependency_overrides.clear()


def test_hairdresser_bookings_success_only_own_bookings() -> None:
    """GET /api/booking/hairdresser/my returns assigned bookings filtered by params."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    dummy_resp = Response()
    issue_session_cookie(
        dummy_resp,
        actor_id=2,
        actor_type="staff",
        role="PELUQUERO",
        email="sergio@afterlook.com",
        nombre="Sergio",
        profile_complete=True,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
    )
    raw_cookie = dummy_resp.headers["set-cookie"].split(";")[0].split("=")[1]
    client.cookies.set(settings.session_cookie_name, raw_cookie)

    mock_booking = Booking(
        id=101,
        cliente_id=10,
        servicio_id=1,
        peluquero_id=2,
        fecha_inicio=datetime(2026, 10, 15, 11, 0, tzinfo=TZ_AR),
        duracion_minutos=30,
        estado=BookingStatus.CONFIRMED.value,
        canal_reserva=BookingChannel.WEB.value,
        precio_estimado=Decimal("2000.00"),
        notas_cliente="Corte moderno",
        created_at=datetime(2026, 10, 14, 10, 0, tzinfo=TZ_AR),
    )
    mock_booking.cliente = Client(
        id=10,
        nombre="Juan Perez",
        email_google="juan@example.com",
        telefono="+5491144445555",
        whatsapp="+5491144445555",
    )
    mock_booking.servicio = Service(
        id=1,
        nombre="Corte clásico",
        tipo_servicio="PELUQUERIA",
        duracion_minutos=30,
        precio_base=Decimal("2000.00"),
    )
    mock_booking.fecha_fin = datetime(2026, 10, 15, 11, 30, tzinfo=TZ_AR)

    with patch(
        "app.modules.booking.router.get_hairdresser_bookings",
        new_callable=AsyncMock,
        return_value=[mock_booking],
    ) as mock_get:
        response = client.get(
            "/api/booking/hairdresser/my?fecha=2026-10-15&estado=CONFIRMADA"
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 101
    assert data[0]["cliente"]["nombre"] == "Juan Perez"
    assert data[0]["cliente"]["telefono"] == "+5491144445555"
    assert data[0]["cliente"]["whatsapp"] == "+5491144445555"
    assert data[0]["cliente"]["email"] == "juan@example.com"
    assert data[0]["servicio_nombre"] == "Corte clásico"
    assert data[0]["tipo_servicio"] == "PELUQUERIA"
    assert data[0]["duracion_minutos"] == 30
    assert data[0]["precio_estimado"] == "2000.00"
    assert data[0]["estado"] == "CONFIRMADA"
    assert data[0]["notas_cliente"] == "Corte moderno"
    mock_get.assert_called_once_with(
        ANY,
        hairdresser_id=2,
        fecha=date(2026, 10, 15),
        estado="CONFIRMADA",
    )

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_hairdresser_update_status_success_and_history() -> None:
    """Updates booking status, inserts BookingHistory audit record, and returns 200."""
    # 1. Test domain service layer
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_booking = Booking(
        id=101,
        cliente_id=10,
        servicio_id=1,
        peluquero_id=2,
        fecha_inicio=datetime(2026, 10, 15, 11, 0, tzinfo=TZ_AR),
        duracion_minutos=30,
        estado=BookingStatus.CONFIRMED.value,
        canal_reserva=BookingChannel.WEB.value,
        precio_estimado=Decimal("2000.00"),
    )
    mock_booking.cliente = Client(
        id=10,
        nombre="Juan",
        email_google="juan@example.com",
    )
    mock_booking.servicio = Service(
        id=1,
        nombre="Corte",
        tipo_servicio="PELUQUERIA",
    )

    mock_scalar_result = MagicMock()
    mock_scalar_result.unique.return_value.first.return_value = mock_booking
    mock_session.scalars.return_value = mock_scalar_result

    updated = await update_booking_status_by_hairdresser(
        mock_session,
        hairdresser_id=2,
        booking_id=101,
        nuevo_estado=BookingStatus.ATTENDED.value,
        motivo="Cliente atendido puntualmente",
    )

    assert updated.estado == BookingStatus.ATTENDED.value
    assert mock_session.add.call_count == 1
    history_entry = mock_session.add.call_args[0][0]
    assert isinstance(history_entry, BookingHistory)
    assert history_entry.reserva_id == 101
    assert history_entry.estado_anterior == BookingStatus.CONFIRMED.value
    assert history_entry.estado_nuevo == BookingStatus.ATTENDED.value
    assert history_entry.motivo == "Cliente atendido puntualmente"
    assert history_entry.realizado_por_usuario_id == 2
    mock_session.commit.assert_awaited_once()

    # 2. Test HTTP router endpoint
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    dummy_resp = Response()
    issue_session_cookie(
        dummy_resp,
        actor_id=2,
        actor_type="staff",
        role="PELUQUERO",
        email="sergio@afterlook.com",
        nombre="Sergio",
        profile_complete=True,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
    )
    raw_cookie = dummy_resp.headers["set-cookie"].split(";")[0].split("=")[1]
    client.cookies.set(settings.session_cookie_name, raw_cookie)

    mock_booking.fecha_fin = datetime(2026, 10, 15, 11, 30, tzinfo=TZ_AR)
    mock_booking.created_at = datetime(2026, 10, 14, 10, 0, tzinfo=TZ_AR)

    with patch(
        "app.modules.booking.router.update_booking_status_by_hairdresser",
        new_callable=AsyncMock,
        return_value=mock_booking,
    ):
        response = client.patch(
            "/api/booking/hairdresser/bookings/101/status",
            json={"estado": "ASISTIO", "motivo": "Cliente atendido puntualmente"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 101
    assert data["estado"] == "ASISTIO"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_hairdresser_update_status_forbidden_if_not_own_booking() -> None:
    """Raises 403 when hairdresser attempts to modify another stylist's reservation."""
    mock_session = AsyncMock()
    mock_booking = Booking(
        id=102,
        cliente_id=10,
        servicio_id=1,
        peluquero_id=99,  # Different hairdresser
        estado=BookingStatus.CONFIRMED.value,
    )
    mock_scalar_result = MagicMock()
    mock_scalar_result.unique.return_value.first.return_value = mock_booking
    mock_session.scalars.return_value = mock_scalar_result

    with pytest.raises(HTTPException) as exc_info:
        await update_booking_status_by_hairdresser(
            mock_session,
            hairdresser_id=2,
            booking_id=102,
            nuevo_estado=BookingStatus.ATTENDED.value,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "NOT_YOUR_BOOKING"

    # Also test booking not found
    mock_scalar_result.unique.return_value.first.return_value = None
    with pytest.raises(HTTPException) as not_found_exc:
        await update_booking_status_by_hairdresser(
            mock_session,
            hairdresser_id=2,
            booking_id=999,
            nuevo_estado=BookingStatus.ATTENDED.value,
        )
    assert not_found_exc.value.status_code == 404
    assert not_found_exc.value.detail == "BOOKING_NOT_FOUND"

    # Also test invalid status
    mock_scalar_result.unique.return_value.first.return_value = mock_booking
    mock_booking.peluquero_id = 2
    with pytest.raises(HTTPException) as invalid_exc:
        await update_booking_status_by_hairdresser(
            mock_session,
            hairdresser_id=2,
            booking_id=102,
            nuevo_estado="ESTADO_INEXISTENTE",
        )
    assert invalid_exc.value.status_code == 400
    assert invalid_exc.value.detail == "INVALID_STATUS"
