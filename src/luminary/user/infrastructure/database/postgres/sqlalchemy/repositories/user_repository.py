from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from luminary.user.application.dtos.profile import ExternalProfile, UserProfile
from luminary.user.application.interfaces.user_repository import IUserRepository
from luminary.user.infrastructure.database.postgres.sqlalchemy.models.user_base import (
    UserBase,
)


class UserRepository(IUserRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

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
            )
            .returning(UserBase)
        )
        user: UserBase = await self.executor.execute_scalar(statement)
        return UserProfile(user.user_id, user.name, user.email or "")
