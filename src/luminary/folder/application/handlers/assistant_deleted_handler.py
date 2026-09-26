from common.application.interfaces.handlers.handler import IEventHandler

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.assistant.domain.events.events import AssistantDeletedEvent
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)


class FolderAssistantDeletedHandler(IEventHandler[AssistantDeletedEvent]):
    """Clears assistant_id reference in folders when an assistant is soft-deleted."""

    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def handle(self, event: AssistantDeletedEvent) -> None:
        await self.folder_repository.clear_assistant_reference(
            AssistantId(event.assistant_id)
        )
