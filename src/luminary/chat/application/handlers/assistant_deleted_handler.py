from common.application.interfaces.handlers.handler import IEventHandler

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.assistant.domain.events.events import AssistantDeletedEvent
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)


class ChatAssistantDeletedHandler(IEventHandler[AssistantDeletedEvent]):
    """Clears assistant_id reference in chats when an assistant is soft-deleted."""

    def __init__(self, chat_repository: IChatRepository) -> None:
        self.chat_repository = chat_repository

    async def handle(self, event: AssistantDeletedEvent) -> None:
        await self.chat_repository.clear_assistant_reference(
            AssistantId(event.assistant_id)
        )
