from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert

from luminary.user.application.dtos.profile import ExternalProfile, UserProfile
from luminary.user.application.interfaces.user_repository import IUserRepository
from luminary.user.infrastructure.database.postgres.sqlalchemy.models.user_base import (
    UserBase,
)


class UserRepository(IUserRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_subject(self, subject: str) -> UserProfile | None:
        user = await self.executor.execute_scalar_one(
            select(UserBase).where(UserBase.zitadel_sub == subject)
        )
        if user is None:
            return None
        return UserProfile(user.user_id, user.name, user.email or "")

    async def upsert(self, user_id: UUID, profile: ExternalProfile) -> UserProfile:
        statement = (
            insert(UserBase)
            .values(
                user_id=user_id,
                zitadel_sub=profile.subject,
                name=profile.name,
                email=profile.email,
            )
            .on_conflict_do_update(
                index_elements=[UserBase.zitadel_sub],
                set_={
                    "name": profile.name,
                    "email": profile.email,
                    "updated_at": func.now(),
                },
                where=or_(
                    UserBase.name.is_distinct_from(profile.name),
                    UserBase.email.is_distinct_from(profile.email),
                ),
            )
            .returning(UserBase)
        )
        user: UserBase | None = await self.executor.execute_scalar_one(statement)
        if user is None:
            # A concurrent request inserted/synced the same profile. A separate
            # SELECT sees its committed row even if the INSERT snapshot did not.
            existing = await self.get_by_subject(profile.subject)
            if existing is None:
                raise RuntimeError("User disappeared during profile synchronization")
            return existing
        return UserProfile(user.user_id, user.name, user.email or "")
