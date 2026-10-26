"""Explicitly link an existing local user before their first Zitadel login."""

import argparse
import asyncio
from uuid import UUID

from bootstrap.config import AppConfig
from common.infrastructure.database.sqlalchemy.database import Database
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from luminary.user.infrastructure.database.postgres.sqlalchemy.models.user_base import (
    UserBase,
)


MAX_SUBJECT_LENGTH = 255


async def link_user(session: AsyncSession, user_id: UUID, subject: str) -> None:
    if (
        not subject.strip()
        or len(subject) > MAX_SUBJECT_LENGTH
        or subject != subject.strip()
    ):
        raise ValueError("Provide a valid Zitadel subject")
    statement = (
        update(UserBase)
        .where(UserBase.user_id == user_id, UserBase.zitadel_sub.is_(None))
        .values(zitadel_sub=subject)
        .returning(UserBase.user_id)
    )
    try:
        result = await session.execute(statement)
        if result.scalar_one_or_none() is None:
            raise ValueError("User does not exist or is already linked")
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError(
            "This Zitadel subject is already linked to another user"
        ) from exc


async def run(user_id: UUID, subject: str) -> None:
    database = Database.create(AppConfig.load().db)
    try:
        async with database.get_session_maker()() as session:
            await link_user(session, user_id, subject)
    finally:
        await database.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", required=True, type=UUID)
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()
    try:
        asyncio.run(run(args.user_id, args.subject))
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    print("User linked; their local ID and owned data are unchanged.")


if __name__ == "__main__":
    main()
