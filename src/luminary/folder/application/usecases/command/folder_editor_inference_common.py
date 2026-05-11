from uuid import UUID

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.folder.domain.entity.folder import Folder
from luminary.model.application.prompts.defaults import EMPTY_ASSISTANT_INSTRUCTIONS


def editor_stream_chunk(
    *,
    state: StreamState,
    content: str,
    message_id: UUID,
    status: MessageStatus,
) -> StreamingMessageDTO:
    return StreamingMessageDTO(
        state=state,
        content=content,
        message_id=message_id,
        author=Author.ASSISTANT,
        status=status,
    )


async def folder_inference_system_prompt(
    folder: Folder,
    assistant_repository: IAssistantRepository,
) -> str:
    if folder.assistant_id is not None:
        assistant = await assistant_repository.get_by_id(folder.assistant_id)
        return assistant.instructions.prompt
    return EMPTY_ASSISTANT_INSTRUCTIONS


def folder_source_ids(folder: Folder) -> list[UUID]:
    return [sid.value for sid in folder.sources]
