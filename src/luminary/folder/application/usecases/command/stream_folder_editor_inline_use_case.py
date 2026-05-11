from uuid import uuid4

from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    STREAM_END_CONTENT,
    STREAM_START_CONTENT,
    StreamState,
)
from luminary.chat.domain.enums import MessageStatus
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.stream_folder_editor_inline_use_case import (
    IStreamFolderEditorInlineUseCase,
    StreamFolderEditorInlineCommand,
)
from luminary.folder.application.usecases.command.folder_editor_inference_common import (
    editor_stream_chunk,
    folder_inference_system_prompt,
    folder_source_ids,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.model.application.interfaces.services.engine import (
    IInferenceEngine,
    InferenceMode,
    InferenceRequestDTO,
)


class StreamFolderEditorInlineUseCase(IStreamFolderEditorInlineUseCase):
    def __init__(
        self,
        folder_repository: IFolderRepository,
        access_policy: IFolderAccessPolicy,
        assistant_repository: IAssistantRepository,
        inference_engine: IInferenceEngine,
    ) -> None:
        self._folder_repository = folder_repository
        self._access_policy = access_policy
        self._assistant_repository = assistant_repository
        self._inference_engine = inference_engine

    async def execute(self, command: StreamFolderEditorInlineCommand):
        folder = await self._folder_repository.get_by_id(FolderId(command.folder_id))
        self._access_policy.assert_is_allowed(UserId(command.user_id), folder)

        system_prompt = await folder_inference_system_prompt(
            folder, self._assistant_repository
        )
        source_ids = folder_source_ids(folder)
        stream_id = uuid4()

        yield editor_stream_chunk(
            state=StreamState.START,
            content=STREAM_START_CONTENT,
            message_id=stream_id,
            status=MessageStatus.STREAMING,
        )

        request = InferenceRequestDTO(
            query=command.instruction,
            system_prompt=system_prompt,
            source_ids=source_ids,
            history=(),
            editor_content=command.document_markdown,
            mode=InferenceMode.EDITOR_INLINE,
            chat_source_context=None,
        )
        async for chunk in self._inference_engine.send(request):
            yield editor_stream_chunk(
                state=StreamState.DELTA,
                content=chunk.content,
                message_id=stream_id,
                status=MessageStatus.STREAMING,
            )

        yield editor_stream_chunk(
            state=StreamState.END,
            content=STREAM_END_CONTENT,
            message_id=stream_id,
            status=MessageStatus.COMPLETED,
        )
