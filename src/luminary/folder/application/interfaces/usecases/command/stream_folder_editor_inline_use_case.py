from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamingMessageDTO,
)


@dataclass(frozen=True)
class StreamFolderEditorInlineCommand:
    user_id: UUID
    folder_id: UUID
    instruction: str
    document_markdown: str


class IStreamFolderEditorInlineUseCase(ABC):
    @abstractmethod
    def execute(
        self, command: StreamFolderEditorInlineCommand
    ) -> AsyncGenerator[StreamingMessageDTO, None]: ...
