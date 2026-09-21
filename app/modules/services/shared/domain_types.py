"""Controlled vocabularies shared by the reservation domain models."""

from enum import StrEnum


class ClientAccountStatus(StrEnum):
    """Represent the lifecycle states of a client account."""

    ACTIVE = "ACTIVA"
    SUSPENDED = "SUSPENDIDA"
    INACTIVE = "INACTIVA"


class BookingStatus(StrEnum):
    """Represent the states a reservation can reach."""

    PENDING = "PENDIENTE"
    WAITING = "EN_ESPERA"
    SCHEDULED = "AGENDADA"
    RESERVED = "RESERVADA"
    CONFIRMED = "CONFIRMADA"
    ATTENDED = "ASISTIO"
    NO_SHOW = "NO_ASISTIO"
    CANCELLED = "CANCELADA"


class BookingChannel(StrEnum):
    """Represent the supported reservation intake channels."""

    WEB = "WEB"
    ADMIN = "ADMIN"
    PHONE = "TELEFONO"
    WHATSAPP = "WHATSAPP"


class NotificationChannel(StrEnum):
    """Represent the channels used to deliver notifications."""

    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"


class NotificationStatus(StrEnum):
    """Represent the delivery state of a notification."""

    PENDING = "PENDIENTE"
    SENT = "ENVIADA"
    FAILED = "FALLIDA"


class CalendarProvider(StrEnum):
    """Represent external calendar providers supported by the MVP."""

    GOOGLE_CALENDAR = "GOOGLE_CALENDAR"


class CalendarSyncStatus(StrEnum):
    """Represent the synchronization state of a calendar event."""

    PENDING = "PENDIENTE"
    SYNCHRONIZED = "SINCRONIZADO"
    FAILED = "FALLIDO"
    CANCELLED = "CANCELADO"
