from common.application.interfaces.handlers.handler import IEventHandler

from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.events.events import FolderSourceRemovedEvent
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId
from luminary.source.domain.events.events import SourceDeletedEvent


class FolderSourceDeletedHandler(IEventHandler[SourceDeletedEvent]):
    """Clears source reference in folders when an source is soft-deleted."""

    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def handle(self, event: SourceDeletedEvent) -> None:
        await self.folder_repository.clear_source_reference(SourceId(event.source_id))


class FolderSourceRemovedHandler(IEventHandler[FolderSourceRemovedEvent]):
    """Remove source association when folder source is removed from folder."""

    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def handle(self, event: FolderSourceRemovedEvent) -> None:
        await self.folder_repository.clear_source_association(
            FolderId(event.folder_id), SourceId(event.source_id)
        )
