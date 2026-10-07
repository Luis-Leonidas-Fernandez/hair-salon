"""Schemas and DTOs for calendar module (ADR-018, CU-012)."""

from pydantic import BaseModel


class HairdresserFeedUrlResponse(BaseModel):
    """Response payload for hairdresser feed URL generation."""

    hairdresser_id: int
    token: str
    feed_url: str
    webcal_url: str
    google_subscribe_url: str
