"""Preserve local user IDs while replacing password authentication with Zitadel.

Revision ID: 7b94c2e81a06
Revises: 53efd27aa40a
"""

from alembic import op
import sqlalchemy as sa


revision = "7b94c2e81a06"
down_revision = "53efd27aa40a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("identities", "users")
    op.alter_column("users", "identity_id", new_column_name="user_id")
    op.drop_constraint("identities_username_key", "users", type_="unique")
    op.alter_column("users", "username", new_column_name="name")
    op.add_column("users", sa.Column("zitadel_sub", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.create_unique_constraint("users_zitadel_sub_key", "users", ["zitadel_sub"])
    op.drop_column("users", "password")
    op.drop_table("tokens")


def downgrade() -> None:
    raise RuntimeError(
        "Password hashes and local tokens cannot be restored. "
        "Restore a pre-migration database backup to roll back authentication."
    )
