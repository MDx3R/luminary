from common.application.interfaces.handlers.handler import IEventHandler

from luminary.chat.application.events.chat_events import (
    ChatAddSourceRequestedEvent,
    ChatRemoveSourceRequestedEvent,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.source.domain.entity.source import SourceId


class ChatAddSourceRequestedHandler(IEventHandler[ChatAddSourceRequestedEvent]):
    def __init__(self, chat_repository: IChatRepository) -> None:
        self.chat_repository = chat_repository

    async def handle(self, event: ChatAddSourceRequestedEvent) -> None:
        chat = await self.chat_repository.get_by_id(ChatId(event.chat_id))

        source_id = SourceId(event.source_id)
        if chat.has_source(source_id):
            return

        chat.add_source(source_id)
        await self.chat_repository.save(chat)


class ChatRemoveSourceRequestedHandler(IEventHandler[ChatRemoveSourceRequestedEvent]):
    def __init__(self, chat_repository: IChatRepository) -> None:
        self.chat_repository = chat_repository

    async def handle(self, event: ChatRemoveSourceRequestedEvent) -> None:
        chat = await self.chat_repository.get_by_id(ChatId(event.chat_id))

        source_id = SourceId(event.source_id)
        if not chat.has_source(source_id):
            return

        chat.add_source(source_id)
        await self.chat_repository.save(chat)
