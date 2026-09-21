"""Add database-level protection against overlapping active reservations."""

from collections.abc import Sequence

from alembic import op

revision: str = "20260920_01"
down_revision: str | Sequence[str] | None = "ad58a4b4eef7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add a generated end time and an exclusion constraint for active bookings."""

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE reservas
        ADD COLUMN fecha_fin TIMESTAMP
        GENERATED ALWAYS AS (
            (fecha_inicio AT TIME ZONE 'UTC')
            + (duracion_minutos * INTERVAL '1 minute')
        ) STORED
        """
    )
    op.execute(
        """
        ALTER TABLE reservas
        ADD CONSTRAINT ex_reservas_peluquero_horario_activo
        EXCLUDE USING gist (
            peluquero_id WITH =,
            tsrange(fecha_inicio AT TIME ZONE 'UTC', fecha_fin, '[)') WITH &&
        )
        WHERE (estado IN (
            'PENDIENTE', 'EN_ESPERA', 'AGENDADA', 'RESERVADA', 'CONFIRMADA'
        ))
        """
    )


def downgrade() -> None:
    """Remove reservation overlap protection without removing the extension."""

    op.drop_constraint(
        "ex_reservas_peluquero_horario_activo",
        "reservas",
        type_="exclude",
    )
    op.drop_column("reservas", "fecha_fin")
