from app.infrastructure.database.base import Base
from app.infrastructure.database.metadata import target_metadata
from app.modules.services.shared import models  # noqa: F401


def test_target_metadata_is_application_metadata() -> None:
    assert target_metadata is Base.metadata
    assert {
        "roles",
        "usuarios",
        "clientes",
        "servicios",
        "usuarios_servicios",
        "disponibilidades",
        "reservas",
        "historial_reservas",
        "notificaciones",
        "eventos_calendario",
        "auditoria_cambios",
    } == set(target_metadata.tables)
