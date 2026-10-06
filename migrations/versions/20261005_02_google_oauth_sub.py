"""Add google_sub column to clientes and usuarios tables.

Revision ID: 20261005_02
Revises: 20260920_01
Create Date: 2026-10-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261005_02"
down_revision: str | Sequence[str] | None = "20260920_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique indexed google_sub to clientes and usuarios."""
    op.add_column("clientes", sa.Column("google_sub", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_clientes_google_sub", "clientes", ["google_sub"])
    op.create_index("ix_clientes_google_sub", "clientes", ["google_sub"])

    op.add_column("usuarios", sa.Column("google_sub", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_usuarios_google_sub", "usuarios", ["google_sub"])
    op.create_index("ix_usuarios_google_sub", "usuarios", ["google_sub"])


def downgrade() -> None:
    """Remove google_sub constraints and columns."""
    op.drop_index("ix_usuarios_google_sub", table_name="usuarios")
    op.drop_constraint("uq_usuarios_google_sub", "usuarios", type_="unique")
    op.drop_column("usuarios", "google_sub")

    op.drop_index("ix_clientes_google_sub", table_name="clientes")
    op.drop_constraint("uq_clientes_google_sub", "clientes", type_="unique")
    op.drop_column("clientes", "google_sub")
