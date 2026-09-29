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
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="-1"),
    )
    op.add_column(
        "chats",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="-1"),
    )
    op.execute(
        """UPDATE folders AS f SET sort_order = ranked.position
        FROM (SELECT folder_id,
                     row_number() OVER (
                         PARTITION BY owner_id ORDER BY created_at DESC, folder_id
                     ) - 1 AS position
              FROM folders WHERE NOT is_deleted) AS ranked
        WHERE f.folder_id = ranked.folder_id"""
    )
    op.execute(
        """UPDATE chats AS c SET sort_order = ranked.position
        FROM (SELECT chat_id,
                     row_number() OVER (
                         PARTITION BY owner_id, folder_id
                         ORDER BY created_at DESC, chat_id
                     ) - 1 AS position
              FROM chats WHERE NOT is_deleted) AS ranked
        WHERE c.chat_id = ranked.chat_id"""
    )


def downgrade() -> None:
    op.drop_column("chats", "sort_order")
    op.drop_column("folders", "sort_order")
    op.drop_column("folders", "collapsed")
