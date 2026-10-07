"""HTTP router for Google Calendar integration (ADR-018, CU-012)."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.infrastructure.database.session import get_db_session
from app.modules.calendar.schemas import HairdresserFeedUrlResponse
from app.modules.calendar.security import (
    generate_hairdresser_feed_token,
    verify_hairdresser_feed_token,
)
from app.modules.calendar.service import get_hairdresser_calendar_feed
from app.modules.identity.session import extract_session

logger = logging.getLogger("afterlook.calendar")

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.get("/hairdresser/my-feed-url", response_model=HairdresserFeedUrlResponse)
async def get_my_calendar_feed_url(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> HairdresserFeedUrlResponse:
    """Retorna la URL del feed iCalendar para el peluquero o admin."""
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

    if session.actor_type != "staff" or session.role not in ("PELUQUERO", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SOLO_STAFF_AUTORIZADO",
        )

    hairdresser_id = session.sub
    token = generate_hairdresser_feed_token(hairdresser_id, settings.secret_key)

    base_url = (
        settings.google_redirect_uri.split("/auth")[0]
        if settings.google_redirect_uri
        else str(request.base_url).rstrip("/")
    )
    feed_path = f"/api/calendar/hairdresser/{hairdresser_id}/feed.ics?token={token}"
    feed_url = f"{base_url}{feed_path}" if base_url else feed_path
    webcal_url = feed_url.replace("https://", "webcal://").replace(
        "http://", "webcal://"
    )
    if not webcal_url.startswith("webcal://"):
        webcal_url = f"webcal://{webcal_url.lstrip('/')}"

    google_subscribe_url = (
        f"https://calendar.google.com/calendar/r/settings/addbyurl?cid={feed_url}"
    )

    return HairdresserFeedUrlResponse(
        hairdresser_id=hairdresser_id,
        token=token,
        feed_url=feed_url,
        webcal_url=webcal_url,
        google_subscribe_url=google_subscribe_url,
    )


@router.get("/hairdresser/{hairdresser_id}/feed.ics")
async def get_hairdresser_feed(
    hairdresser_id: int,
    token: str = Query(..., description="Token de seguridad HMAC"),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    """Endpoint público seguro para consulta de Google Calendar / Apple Calendar."""
    if not verify_hairdresser_feed_token(hairdresser_id, token, settings.secret_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TOKEN_CALENDARIO_INVALIDO",
        )

    try:
        ics_content = await get_hairdresser_calendar_feed(
            db=db,
            hairdresser_id=hairdresser_id,
            salon_name=settings.salon_name,
            salon_address=settings.salon_address,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PELUQUERO_NO_ENCONTRADO_O_INACTIVO",
        )

    logger.info(
        "calendar_feed_accessed hairdresser_id=%d status=200",
        hairdresser_id,
    )

    filename = f"afterlook-agenda-{hairdresser_id}.ics"
    cache_max_age = settings.calendar_feed_ttl_minutes * 60
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": f"private, max-age={cache_max_age}",
        },
    )
