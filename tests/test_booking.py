"""Tests for booking catalog, availability and reservation lifecycle (CU-003)."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo

from fastapi import Response
from fastapi.testclient import TestClient

from app.config.settings import Settings, get_settings
from app.main import app
from app.modules.booking.schemas import (
    TimeSlot,
)
from app.modules.identity.session import issue_session_cookie
from app.modules.services.shared.domain_types import BookingChannel, BookingStatus
from app.modules.services.shared.models import (
    Booking,
    Role,
    Service,
    User,
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


def test_list_services_endpoint() -> None:
    """GET /api/booking/services returns active services."""
    mock_services = [
        Service(
            id=1,
            nombre="Corte de cabello",
            descripcion="Corte clásico",
            tipo_servicio="PELUQUERIA",
            duracion_minutos=60,
            precio_base=Decimal("1500.00"),
            activo=True,
        ),
        Service(
            id=2,
            nombre="Barbería",
            descripcion="Arreglo de barba",
            tipo_servicio="BARBERIA",
            duracion_minutos=30,
            precio_base=Decimal("1000.00"),
            activo=True,
        ),
    ]

    client = TestClient(app)
    with patch(
        "app.modules.booking.router.get_active_services",
        new_callable=AsyncMock,
        return_value=mock_services,
    ):
        response = client.get("/api/booking/services")

    assert response.status_code == 200
    services = response.json()
    assert len(services) == 2
    assert services[0]["nombre"] == "Corte de cabello"
    assert services[1]["nombre"] == "Barbería"


def test_list_hairdressers_endpoint() -> None:
    """GET /api/booking/hairdressers returns active hairdressers."""
    peluquero_role = Role(id=2, nombre="PELUQUERO", activo=True)
    mock_hairdressers = [
        User(
            id=2,
            nombre_completo="Sergio",
            email_google="sergio@afterlook.com",
            rol_id=2,
            rol=peluquero_role,
            activo=True,
        ),
        User(
            id=3,
            nombre_completo="Raul",
            email_google="raul@afterlook.com",
            rol_id=2,
            rol=peluquero_role,
            activo=True,
        ),
    ]

    client = TestClient(app)
    with patch(
        "app.modules.booking.router.get_active_hairdressers",
        new_callable=AsyncMock,
        return_value=mock_hairdressers,
    ):
        response = client.get("/api/booking/hairdressers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre_completo"] == "Sergio"
    assert data[1]["nombre_completo"] == "Raul"


def test_check_availability_endpoint() -> None:
    """GET /api/booking/availability returns slot list."""
    mock_slots = [
        TimeSlot(hora="09:30", disponible=True),
        TimeSlot(hora="10:00", disponible=False),
        TimeSlot(hora="10:30", disponible=True),
    ]

    client = TestClient(app)
    with patch(
        "app.modules.booking.router.get_hairdresser_availability",
        new_callable=AsyncMock,
        return_value=mock_slots,
    ):
        response = client.get(
            "/api/booking/availability?peluquero_id=2&fecha=2026-10-15&duracion_minutos=60"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["peluquero_id"] == 2
    assert len(data["slots"]) == 3
    assert data["slots"][0]["hora"] == "09:30"
    assert data["slots"][0]["disponible"] is True
    assert data["slots"][1]["disponible"] is False


def test_reserve_unauthenticated_returns_401() -> None:
    """POST /api/booking/reserve returns 401 when no session cookie is provided."""
    client = TestClient(app)
    payload = {
        "servicio_id": 1,
        "peluquero_id": 2,
        "fecha": "2026-10-15",
        "hora": "10:30",
    }
    response = client.post("/api/booking/reserve", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "NOT_AUTHENTICATED"


def test_reserve_staff_actor_returns_403() -> None:
    """POST /api/booking/reserve returns 403 when authenticated as staff."""
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

    payload = {
        "servicio_id": 1,
        "peluquero_id": 2,
        "fecha": "2026-10-15",
        "hora": "10:30",
    }
    response = client.post("/api/booking/reserve", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "SOLO_CLIENTES_PUEDEN_RESERVAR"

    app.dependency_overrides.clear()


def test_reserve_client_success() -> None:
    """POST /api/booking/reserve creates appointment and returns 201."""
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

    mock_booking = Booking(
        id=77,
        cliente_id=1,
        servicio_id=1,
        peluquero_id=2,
        fecha_inicio=datetime(2026, 10, 15, 10, 30, tzinfo=TZ_AR),
        duracion_minutos=60,
        estado=BookingStatus.CONFIRMED.value,
        canal_reserva=BookingChannel.WEB.value,
        precio_estimado=Decimal("1500.00"),
        notas_cliente="Sin notas",
        created_at=datetime.now(TZ_AR),
    )
    mock_booking.servicio = Service(
        id=1, nombre="Corte de cabello", tipo_servicio="PELUQUERIA", duracion_minutos=60
    )
    mock_booking.peluquero = User(
        id=2, nombre_completo="Sergio", email_google="sergio@afterlook.com", rol_id=2
    )

    with patch(
        "app.modules.booking.router.create_booking",
        new_callable=AsyncMock,
        return_value=mock_booking,
    ):
        response = client.post(
            "/api/booking/reserve",
            json={
                "servicio_id": 1,
                "peluquero_id": 2,
                "fecha": "2026-10-15",
                "hora": "10:30",
                "notas_cliente": "Sin notas",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 77
    assert data["cliente_id"] == 1
    assert data["servicio_nombre"] == "Corte de cabello"
    assert data["peluquero_nombre"] == "Sergio"
    assert data["estado"] == "CONFIRMADA"

    app.dependency_overrides.clear()
