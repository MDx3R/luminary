from importlib import import_module
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Connection, inspect, text


def migrate_legacy_user(connection: Connection) -> None:
    # A separate schema makes this independent of the current ORM metadata.
    connection.execute(text("CREATE SCHEMA auth_migration_test"))
    connection.execute(text("SET LOCAL search_path TO auth_migration_test"))
    connection.execute(
        text(
            """
        CREATE TABLE identities (
            identity_id UUID PRIMARY KEY,
            username VARCHAR NOT NULL UNIQUE,
            password VARCHAR NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """
        )
    )
    connection.execute(text("CREATE TABLE tokens (token_id UUID PRIMARY KEY)"))
    connection.execute(text("CREATE TABLE folders (owner_id UUID NOT NULL)"))
    user_id = uuid4()
    connection.execute(
        text(
            "INSERT INTO identities (identity_id, username, password) VALUES (:id, 'legacy', 'hash')"
        ),
        {"id": user_id},
    )
    connection.execute(
        text("INSERT INTO folders (owner_id) VALUES (:id)"), {"id": user_id}
    )
    migration = import_module("migrations.versions.7b94c2e81a06_zitadel_users")
    with Operations.context(MigrationContext.configure(connection)):
        migration.upgrade()

    row = connection.execute(
        text("SELECT user_id, name, zitadel_sub, email FROM users")
    ).one()
    assert row == (user_id, "legacy", None, None)
    assert connection.scalar(text("SELECT owner_id FROM folders")) == user_id
    inspector = inspect(connection)
    assert "password" not in {
        column["name"]
        for column in inspector.get_columns("users", schema="auth_migration_test")
    }
    assert not inspector.has_table("tokens", schema="auth_migration_test")
    with pytest.raises(RuntimeError, match="backup"):
        migration.downgrade()


@pytest.mark.asyncio
async def test_migration_preserves_legacy_user_and_ownership(engine):
    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            await connection.run_sync(migrate_legacy_user)
            await transaction.rollback()


def migrate_empty_database(connection: Connection) -> None:
    connection.execute(text("CREATE SCHEMA auth_fresh_install_test"))
    connection.execute(text("SET LOCAL search_path TO auth_fresh_install_test"))
    revisions = [
        "1c72f6123940_init",
        "16cb271c01ba_idp",
        "ae35c1701f10_assistants_tags_and_user_id",
        "53efd27aa40a_drop_model_id_for_chat_and_message",
        "7b94c2e81a06_zitadel_users",
    ]
    with Operations.context(MigrationContext.configure(connection)):
        for revision in revisions:
            import_module(f"migrations.versions.{revision}").upgrade()
    tables = inspect(connection).get_table_names(schema="auth_fresh_install_test")
    assert "users" in tables
    assert "identities" not in tables
    assert "tokens" not in tables
    assert "chats" in tables


@pytest.mark.asyncio
async def test_all_migrations_support_a_fresh_install(engine):
    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            await connection.run_sync(migrate_empty_database)
            await transaction.rollback()
