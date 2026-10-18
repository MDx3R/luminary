"""Persist folder and chat ordering and folder collapsed state.

Revision ID: 6d42f8c91b03
Revises: 53efd27aa40a
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "6d42f8c91b03"
down_revision: str | Sequence[str] | None = "53efd27aa40a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "folders",
        sa.Column("collapsed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "folders",
        sa.Column("order_key", sa.String(collation="C"), nullable=True),
    )
    op.add_column(
        "chats",
        sa.Column("order_key", sa.String(collation="C"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chats", "order_key")
    op.drop_column("folders", "order_key")
    op.drop_column("folders", "collapsed")
