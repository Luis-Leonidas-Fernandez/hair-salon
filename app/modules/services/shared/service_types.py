"""Controlled vocabulary for service classifications."""

from enum import StrEnum


class ServiceType(StrEnum):
    """Represent the stable business classifications allowed for services."""

    BARBERIA = "BARBERIA"
    PELUQUERIA = "PELUQUERIA"
