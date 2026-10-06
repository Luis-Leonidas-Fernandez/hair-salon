import re
from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class CompleteProfileRequest(BaseModel):
    """Payload for completing client contact profile (CU-002)."""

    telefono: str
    whatsapp: str | None = None
    fecha_nacimiento: date | None = None

    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 6 or len(cleaned) > 30:
            raise ValueError("El teléfono debe tener entre 6 y 30 caracteres.")
        if not re.match(r"^\+?[0-9\s\-\(\)]+$", cleaned):
            raise ValueError(
                "El formato de teléfono contiene caracteres no permitidos."
            )
        return cleaned

    @field_validator("whatsapp")
    @classmethod
    def validate_whatsapp(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        if len(cleaned) < 6 or len(cleaned) > 30:
            raise ValueError("El WhatsApp debe tener entre 6 y 30 caracteres.")
        if not re.match(r"^\+?[0-9\s\-\(\)]+$", cleaned):
            raise ValueError(
                "El formato de WhatsApp contiene caracteres no permitidos."
            )
        return cleaned


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
