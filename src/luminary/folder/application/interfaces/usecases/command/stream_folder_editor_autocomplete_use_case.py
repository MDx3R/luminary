from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamingMessageDTO,
)


@dataclass(frozen=True)
class StreamFolderEditorAutocompleteCommand:
    user_id: UUID
    folder_id: UUID
    text_before_cursor: str
    text_after_cursor: str


class IStreamFolderEditorAutocompleteUseCase(ABC):
    @abstractmethod
    def execute(
        self, command: StreamFolderEditorAutocompleteCommand
    ) -> AsyncGenerator[StreamingMessageDTO, None]: ...
