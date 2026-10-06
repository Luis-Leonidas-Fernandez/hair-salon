"""Pydantic data schemas for identity and session representation."""

from pydantic import BaseModel, ConfigDict


class SessionPayload(BaseModel):
    """Payload decoded from the canonical session cookie."""

    sub: int
    actor_type: str
    role: str
    email: str
    nombre: str
    profile_complete: bool

    model_config = ConfigDict(frozen=True)


class CurrentUserResponse(BaseModel):
    """Public representation of the authenticated session identity."""

    id: int
    actor_type: str
    role: str
    email: str
    nombre: str
    profile_complete: bool

    model_config = ConfigDict(from_attributes=True)
