"""Domain errors shared by the service module."""


class SeedValidationError(ValueError):
    """Raised when initial data would make the seed unsafe to execute."""
