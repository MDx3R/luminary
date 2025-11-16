from collections.abc import Sequence
from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.chat.application.interfaces.repositories.chat_read_repository import (
    IChatReadRepository,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    ChatDTO,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    ChatListItemDTO,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
)


class ChatReadRepository(IChatReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id_for_user(self, chat_id: UUID, user_id: UUID) -> ChatDTO | None:
        query = select(ChatBase).where(
            ChatBase.chat_id == chat_id,
            ChatBase.user_id == user_id,
        )

        try:
            result = await self.executor.execute_scalar_one(query)
        except Exception:
            return None

        if result is None:
            return None

        return ChatDTO(
            chat_id=result.chat_id,
            user_id=result.user_id,
            folder_id=result.folder_id,
            name=result.name,
            model_id=result.model_id,
            system_prompt=result.system_prompt,
            max_context_messages=result.max_context_messages,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    async def get_by_user_id(self, user_id: UUID) -> Sequence[ChatListItemDTO]:
        query = (
            select(ChatBase)
            .where(ChatBase.user_id == user_id)
            .order_by(ChatBase.updated_at.desc())
        )
        results = await self.executor.execute_scalar_many(query)

        return [
            ChatListItemDTO(
                chat_id=chat.chat_id,
                name=chat.name,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
            )
            for chat in results
        ]

    async def get_by_folder_id_for_user(
        self, folder_id: UUID, user_id: UUID
    ) -> Sequence[ChatListItemDTO]:
        query = (
            select(ChatBase)
            .join(FolderBase, ChatBase.folder_id == FolderBase.folder_id)
            .where(
                ChatBase.folder_id == folder_id,
                FolderBase.user_id == user_id,
            )
            .order_by(ChatBase.updated_at.desc())
        )
        results = await self.executor.execute_scalar_many(query)

        return [
            ChatListItemDTO(
                chat_id=chat.chat_id,
                name=chat.name,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
            )
            for chat in results
        ]
