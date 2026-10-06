"""Schemas for booking module (CU-003)."""

import re
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.services.shared.domain_types import BookingStatus


class ServiceResponse(BaseModel):
    """Catalog service available for booking."""

    id: int
    nombre: str
    descripcion: str | None = None
    tipo_servicio: str
    duracion_minutos: int
    precio_base: Decimal

    model_config = ConfigDict(from_attributes=True)


class HairdresserResponse(BaseModel):
    """Staff stylist available for booking."""

    id: int
    nombre_completo: str
    email_google: str

    model_config = ConfigDict(from_attributes=True)


class TimeSlot(BaseModel):
    """Individual 30-minute candidate time slot."""

    hora: str
    disponible: bool


class AvailabilityResponse(BaseModel):
    """Hairdresser availability schedule on a specific date."""

    fecha: date
    peluquero_id: int
    slots: list[TimeSlot]


class CreateBookingRequest(BaseModel):
    """Payload to request a new hair salon booking."""

    servicio_id: int
    peluquero_id: int
    fecha: date
    hora: str
    notas_cliente: str | None = None

    @field_validator("hora")
    @classmethod
    def validate_hora_format(cls, v: str) -> str:
        clean = v.strip()
        if not re.match(r"^\d{2}:\d{2}$", clean):
            raise ValueError("El formato de hora debe ser HH:MM (ej. 10:30).")
        hours, minutes = map(int, clean.split(":"))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError("Hora o minutos fuera de rango válido.")
        return clean

    @field_validator("notas_cliente")
    @classmethod
    def validate_notas(cls, v: str | None) -> str | None:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        if len(clean) > 500:
            raise ValueError("Las notas no pueden superar los 500 caracteres.")
        return clean


class BookingResponse(BaseModel):
    """Canonical representation of a salon reservation."""

    id: int
    cliente_id: int
    servicio_id: int
    servicio_nombre: str
    peluquero_id: int
    peluquero_nombre: str
    fecha_inicio: datetime
    duracion_minutos: int
    estado: str
    canal_reserva: str
    notas_cliente: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HairdresserBookingClient(BaseModel):
    """Client contact details for hairdresser appointment view (CU-010)."""

    id: int
    nombre: str
    telefono: str | None = None
    whatsapp: str | None = None
    email: str

    model_config = ConfigDict(from_attributes=True)


class HairdresserBookingResponse(BaseModel):
    """Detailed reservation data presented to the stylist (CU-010)."""

    id: int
    cliente: HairdresserBookingClient
    servicio_id: int
    servicio_nombre: str
    tipo_servicio: str
    duracion_minutos: int
    precio_estimado: Decimal
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    canal_reserva: str
    notas_cliente: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateBookingStatusRequest(BaseModel):
    """Payload to transition appointment lifecycle status by hairdresser (CU-011)."""

    estado: str
    motivo: str | None = None

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: str) -> str:
        clean = v.strip().upper()
        valid_statuses = {s.value for s in BookingStatus}
        if clean not in valid_statuses:
            allowed = sorted(valid_statuses)
            raise ValueError(f"Estado '{clean}' no es válido. Opciones: {allowed}")
        return clean
