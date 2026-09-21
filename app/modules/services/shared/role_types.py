"""Controlled vocabulary for internal user roles."""

from enum import StrEnum


class InternalRole(StrEnum):
    """Represent the stable roles recognized by the MVP authorization model."""

    ADMIN = "ADMIN"
    PELUQUERO = "PELUQUERO"
    CLIENTE = "CLIENTE"
