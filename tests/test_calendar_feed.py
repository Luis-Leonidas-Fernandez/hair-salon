"""Comprehensive test suite for Google Calendar Integration (ADR-018, CU-012)."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo

import pytest
from fastapi import Response
from fastapi.testclient import TestClient

from app.config.settings import Settings, get_settings
from app.main import app
from app.modules.calendar.ics_builder import (
    _escape_ics_text,
    _fold_line,
    _format_ics_datetime,
    build_hairdresser_ics_feed,
)
from app.modules.calendar.security import (
    generate_hairdresser_feed_token,
    verify_hairdresser_feed_token,
)
from app.modules.calendar.service import get_hairdresser_calendar_feed
from app.modules.identity.session import issue_session_cookie
from app.modules.services.shared.domain_types import BookingStatus
from app.modules.services.shared.models import Booking, Client, Service, User

SECRET_KEY = "test-calendar-secret-key-at-least-32-bytes"
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
        salon_name="After Look",
        salon_address="Av. Corrientes 1234, CABA, Argentina",
        salon_timezone="America/Argentina/Buenos_Aires",
        calendar_feed_ttl_minutes=60,
    )


def test_token_generation_and_verification() -> None:
    """Verify deterministic token generation and constant-time validation."""
    secret = "my-secure-app-secret-123456789012"
    token = generate_hairdresser_feed_token(hairdresser_id=3, secret_key=secret)

    # Must be trimmed to 32 characters
    assert len(token) == 32
    assert token.isalnum()

    # Valid token verification succeeds
    assert verify_hairdresser_feed_token(3, token, secret) is True

    # Tampered token fails
    tampered = "0" + token[1:]
    assert verify_hairdresser_feed_token(3, tampered, secret) is False

    # Wrong hairdresser ID fails
    assert verify_hairdresser_feed_token(4, token, secret) is False

    # Wrong secret fails
    assert verify_hairdresser_feed_token(3, token, "different-secret-key") is False

    # Empty or wrong length token fails
    assert verify_hairdresser_feed_token(3, "", secret) is False
    assert verify_hairdresser_feed_token(3, "too-short", secret) is False
    assert verify_hairdresser_feed_token(3, token + "extra", secret) is False


def test_ics_builder_helpers() -> None:
    """Verify datetime formatting, text escaping, and RFC 5545 line folding."""
    # 1. Datetime formatting
    dt_utc = datetime(2026, 10, 15, 14, 30, 0, tzinfo=UTC)
    assert _format_ics_datetime(dt_utc) == "20261015T143000Z"

    # Naive datetime assumed UTC
    dt_naive = datetime(2026, 10, 15, 14, 30, 0)
    assert _format_ics_datetime(dt_naive) == "20261015T143000Z"

    # Timezone-aware datetime converted to UTC
    dt_local = datetime(2026, 10, 15, 11, 30, 0, tzinfo=TZ_AR)
    assert _format_ics_datetime(dt_local) == "20261015T143000Z"

    # 2. Text escaping (RFC 5545 §3.3.11)
    assert _escape_ics_text(None) == ""
    assert _escape_ics_text("") == ""
    assert (
        _escape_ics_text("Corte, Barba; y Lavado\nNota\r\nSegunda fila")
        == "Corte\\, Barba\\; y Lavado\\nNota\\nSegunda fila"
    )
    assert _escape_ics_text(r"Path\To\File") == r"Path\\To\\File"

    # 3. Line folding at 75 bytes (RFC 5545 §3.1)
    short_line = "SUMMARY:Corte Clásico"
    assert _fold_line(short_line) == short_line

    long_line = "DESCRIPTION:" + "A" * 80
    folded = _fold_line(long_line)
    assert "\r\n " in folded
    for part in folded.split("\r\n"):
        assert len(part.encode("utf-8")) <= 75


def test_build_hairdresser_ics_feed_structure() -> None:
    """Verify generated VCALENDAR and VEVENT structures conform to specifications."""
    hairdresser = User(
        id=3,
        nombre_completo="Sergio Barbero",
        email_google="sergio@afterlook.com",
        rol_id=2,
        activo=True,
    )

    client1 = Client(
        id=10,
        nombre="Juan Pérez",
        email_google="juan@example.com",
        telefono="+5491144445555",
        whatsapp="+5491144445555",
    )
    service1 = Service(
        id=1,
        nombre="Corte & Barba",
        tipo_servicio="PELUQUERIA",
        duracion_minutos=45,
        precio_base=Decimal("2500.00"),
    )

    booking_confirmed = Booking(
        id=101,
        cliente_id=10,
        servicio_id=1,
        peluquero_id=3,
        fecha_inicio=datetime(2026, 10, 15, 14, 0, tzinfo=UTC),
        duracion_minutos=45,
        estado=BookingStatus.CONFIRMED.value,
        notas_cliente="Degradé medio",
    )
    booking_confirmed.cliente = client1
    booking_confirmed.servicio = service1

    booking_cancelled = Booking(
        id=102,
        cliente_id=10,
        servicio_id=1,
        peluquero_id=3,
        fecha_inicio=datetime(2026, 10, 15, 16, 0, tzinfo=UTC),
        duracion_minutos=45,
        estado=BookingStatus.CANCELLED.value,
        notas_cliente=None,
    )
    booking_cancelled.cliente = client1
    booking_cancelled.servicio = service1

    ics_content = build_hairdresser_ics_feed(
        hairdresser=hairdresser,
        bookings=[booking_confirmed, booking_cancelled],
        salon_name="After Look",
        salon_address="Av. Corrientes 1234, CABA, Argentina",
    )

    assert ics_content.startswith("BEGIN:VCALENDAR\r\n")
    assert ics_content.endswith("END:VCALENDAR\r\n")
    assert "VERSION:2.0" in ics_content
    assert "PRODID:-//After Look//Agenda Staff v1.0//ES" in ics_content
    assert "CALSCALE:GREGORIAN" in ics_content
    assert "METHOD:PUBLISH" in ics_content
    assert "X-WR-CALNAME:After Look - Sergio Barbero" in ics_content
    assert "X-WR-TIMEZONE:America/Argentina/Buenos_Aires" in ics_content
    assert "REFRESH-INTERVAL;VALUE=DURATION:PT1H" in ics_content
    assert "X-PUBLISHED-TTL:PT1H" in ics_content

    # Events verification
    assert ics_content.count("BEGIN:VEVENT") == 2
    assert ics_content.count("END:VEVENT") == 2
    assert "UID:booking-101@afterlook.com" in ics_content
    assert "UID:booking-102@afterlook.com" in ics_content

    # Start and End dates in UTC
    assert "DTSTART:20261015T140000Z" in ics_content
    assert "DTEND:20261015T144500Z" in ics_content
    assert "DTSTART:20261015T160000Z" in ics_content
    assert "DTEND:20261015T164500Z" in ics_content

    # Summary
    assert "SUMMARY:Corte & Barba - Juan Pérez" in ics_content

    # Statuses
    assert "STATUS:CONFIRMED" in ics_content
    assert "STATUS:CANCELLED" in ics_content

    # Location & Description
    assert "LOCATION:Av. Corrientes 1234\\, CABA\\, Argentina" in ics_content
    assert "Teléfono: +5491144445555" in ics_content
    assert "Notas: Degradé medio" in ics_content


def test_my_feed_url_unauthenticated_returns_401() -> None:
    """GET /api/calendar/hairdresser/my-feed-url returns 401 without cookie."""
    client = TestClient(app)
    response = client.get("/api/calendar/hairdresser/my-feed-url")
    assert response.status_code == 401
    assert response.json()["detail"] == "NOT_AUTHENTICATED"


def test_my_feed_url_client_returns_403() -> None:
    """GET /api/calendar/hairdresser/my-feed-url returns 403 for client actor."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    dummy_resp = Response()
    issue_session_cookie(
        dummy_resp,
        actor_id=10,
        actor_type="cliente",
        role="CLIENTE",
        email="cliente@example.com",
        nombre="Cliente Regular",
        profile_complete=True,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
    )
    raw_cookie = dummy_resp.headers["set-cookie"].split(";")[0].split("=")[1]
    client.cookies.set(settings.session_cookie_name, raw_cookie)

    response = client.get("/api/calendar/hairdresser/my-feed-url")
    assert response.status_code == 403
    assert response.json()["detail"] == "SOLO_STAFF_AUTORIZADO"

    app.dependency_overrides.clear()


def test_my_feed_url_hairdresser_returns_200() -> None:
    """GET /api/calendar/hairdresser/my-feed-url returns 200 with URLs for staff."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    dummy_resp = Response()
    issue_session_cookie(
        dummy_resp,
        actor_id=3,
        actor_type="staff",
        role="PELUQUERO",
        email="peluquero@afterlook.com",
        nombre="Sergio Barbero",
        profile_complete=True,
        secret_key=settings.secret_key,
        cookie_name=settings.session_cookie_name,
    )
    raw_cookie = dummy_resp.headers["set-cookie"].split(";")[0].split("=")[1]
    client.cookies.set(settings.session_cookie_name, raw_cookie)

    response = client.get("/api/calendar/hairdresser/my-feed-url")
    assert response.status_code == 200
    data = response.json()

    expected_token = generate_hairdresser_feed_token(3, settings.secret_key)
    assert data["hairdresser_id"] == 3
    assert data["token"] == expected_token
    expected_path = f"/api/calendar/hairdresser/3/feed.ics?token={expected_token}"
    assert expected_path in data["feed_url"]
    assert (
        "calendar.google.com/calendar/render?cid=webcal"
        in data["google_subscribe_url"]
    )

    # Verify proxy headers (Render/Cloudflare HTTPS)
    response_proxy = client.get(
        "/api/calendar/hairdresser/my-feed-url",
        headers={
            "x-forwarded-proto": "https",
            "x-forwarded-host": "after-look-app.onrender.com",
        },
    )
    assert response_proxy.status_code == 200
    data_proxy = response_proxy.json()
    assert data_proxy["feed_url"].startswith(
        "https://after-look-app.onrender.com/api/calendar"
    )
    assert data_proxy["webcal_url"].startswith(
        "webcal://after-look-app.onrender.com/api/calendar"
    )

    app.dependency_overrides.clear()


def test_feed_ics_invalid_token_returns_403() -> None:
    """GET /api/calendar/hairdresser/{id}/feed.ics with invalid token returns 403."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    bad_url = "/api/calendar/hairdresser/3/feed.ics?token=invalid-token-123456789012"
    response = client.get(bad_url)
    assert response.status_code == 403
    assert response.json()["detail"] == "TOKEN_CALENDARIO_INVALIDO"

    app.dependency_overrides.clear()


def test_feed_ics_valid_token_returns_200_and_calendar_content() -> None:
    """Valid token returns calendar feed with 200 and RFC 5545 headers."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    valid_token = generate_hairdresser_feed_token(3, settings.secret_key)
    mock_ics_body = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "X-WR-CALNAME:After Look - Sergio Barbero\r\n"
        "BEGIN:VEVENT\r\n"
        "SUMMARY:Corte - Test\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    client = TestClient(app)
    with patch(
        "app.modules.calendar.router.get_hairdresser_calendar_feed",
        new_callable=AsyncMock,
        return_value=mock_ics_body,
    ) as mock_feed:
        feed_url = f"/api/calendar/hairdresser/3/feed.ics?token={valid_token}"
        response = client.get(feed_url)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/calendar")
    content_disp = response.headers["content-disposition"]
    assert 'filename="afterlook-agenda-3.ics"' in content_disp
    assert "max-age=3600" in response.headers["cache-control"]
    assert response.text == mock_ics_body

    mock_feed.assert_called_once()
    app.dependency_overrides.clear()


def test_feed_ics_inactive_hairdresser_returns_404() -> None:
    """Inactive or missing hairdresser returns 404."""
    settings = get_test_settings()
    app.dependency_overrides[get_settings] = lambda: settings

    valid_token = generate_hairdresser_feed_token(3, settings.secret_key)

    client = TestClient(app)
    with patch(
        "app.modules.calendar.router.get_hairdresser_calendar_feed",
        new_callable=AsyncMock,
        side_effect=ValueError("HAIRDRESSER_NOT_FOUND_OR_INACTIVE"),
    ):
        feed_url = f"/api/calendar/hairdresser/3/feed.ics?token={valid_token}"
        response = client.get(feed_url)

    assert response.status_code == 404
    assert response.json()["detail"] == "PELUQUERO_NO_ENCONTRADO_O_INACTIVO"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_service_get_hairdresser_calendar_feed_inactive_raises_value_error() -> (
    None
):
    """Service layer raises ValueError if hairdresser is inactive or missing."""
    mock_db = AsyncMock()
    # Case 1: hairdresser not found
    mock_db.get.return_value = None
    with pytest.raises(ValueError, match="HAIRDRESSER_NOT_FOUND_OR_INACTIVE"):
        await get_hairdresser_calendar_feed(
            db=mock_db,
            hairdresser_id=99,
            salon_name="After Look",
            salon_address="Av. Corrientes 1234",
        )

    # Case 2: hairdresser inactive
    inactive_user = User(
        id=4,
        nombre_completo="Inactivo",
        activo=False,
        email_google="in@test.com",
        rol_id=2,
    )
    mock_db.get.return_value = inactive_user
    with pytest.raises(ValueError, match="HAIRDRESSER_NOT_FOUND_OR_INACTIVE"):
        await get_hairdresser_calendar_feed(
            db=mock_db,
            hairdresser_id=4,
            salon_name="After Look",
            salon_address="Av. Corrientes 1234",
        )
