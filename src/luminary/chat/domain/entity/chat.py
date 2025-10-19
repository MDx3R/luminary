from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


@dataclass(frozen=True)
class ChatInfo:
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Chat name cannot be empty")


@dataclass(frozen=True)
class ChatSettings:
    model_id: UUID
    system_prompt: str | None
    max_context_messages: int

    def __post_init__(self) -> None:
        if self.system_prompt and not self.system_prompt.strip():
            raise InvariantViolationError("System prompt cannot be empty")
        if self.max_context_messages <= 0:
            raise InvariantViolationError(
                "Number of context messages cannot be non-positive"
            )


@dataclass
class Chat:
    chat_id: UUID
    user_id: UUID
    folder_id: UUID | None
    info: ChatInfo
    settings: ChatSettings
    created_at: DateTime

    def change_name(self, new_name: str) -> None:
        self.info = ChatInfo(new_name)

    def change_settings(self, new_settings: ChatSettings) -> None:
        self.settings = new_settings

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        chat_id: UUID,
        user_id: UUID,
        folder_id: UUID | None,
        name: str,
        settings: ChatSettings,
        created_at: DateTime,
    ) -> Self:
        return cls(
            chat_id=chat_id,
            user_id=user_id,
            folder_id=folder_id,
            info=ChatInfo(name=name),
            settings=settings,
            created_at=created_at,
        )
