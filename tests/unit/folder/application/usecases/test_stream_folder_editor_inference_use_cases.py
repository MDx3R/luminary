import asyncio
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamState,
)
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.stream_folder_editor_autocomplete_use_case import (
    StreamFolderEditorAutocompleteCommand,
)
from luminary.folder.application.interfaces.usecases.command.stream_folder_editor_inline_use_case import (
    StreamFolderEditorInlineCommand,
)
from luminary.folder.application.usecases.command.stream_folder_editor_autocomplete_use_case import (
    StreamFolderEditorAutocompleteUseCase,
)
from luminary.folder.application.usecases.command.stream_folder_editor_inline_use_case import (
    StreamFolderEditorInlineUseCase,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.model.application.interfaces.services.engine import (
    EngineStreamingResponse,
    IInferenceEngine,
    InferenceMode,
    InferenceRequestDTO,
)
from luminary.source.domain.entity.source import SourceId


async def _mock_stream(*chunks: str):
    for c in chunks:
        yield EngineStreamingResponse(content=c)


class TestStreamFolderEditorInlineUseCase:
    def test_streams_and_builds_inference_request(self) -> None:
        async def run() -> None:
            user_id = uuid4()
            folder_id = uuid4()
            source_id = uuid4()
            folder = make_folder(folder_id=folder_id, owner_id=user_id)
            folder.add_source(SourceId(source_id))

            folder_repository: AsyncMock = AsyncMock(
                spec=IFolderRepository,
                get_by_id=AsyncMock(return_value=folder),
            )
            access_policy: Mock = Mock(spec=IFolderAccessPolicy)
            assistant_repository: AsyncMock = AsyncMock()
            inference_engine: Mock = Mock(spec=IInferenceEngine)
            inference_engine.send.return_value = _mock_stream("ok")

            use_case = StreamFolderEditorInlineUseCase(
                folder_repository=folder_repository,
                access_policy=access_policy,
                assistant_repository=assistant_repository,
                inference_engine=inference_engine,
            )

            command = StreamFolderEditorInlineCommand(
                user_id=user_id,
                folder_id=folder_id,
                instruction="Shorten intro",
                document_markdown="# Doc",
            )
            chunks = [c async for c in use_case.execute(command)]

            folder_repository.get_by_id.assert_awaited_once_with(FolderId(folder_id))
            access_policy.assert_is_allowed.assert_called_once_with(
                UserId(user_id), folder
            )
            inference_engine.send.assert_called_once()
            request = inference_engine.send.call_args[0][0]
            assert isinstance(request, InferenceRequestDTO)
            assert request.history == ()
            assert request.query == "Shorten intro"
            assert request.editor_content == "# Doc"
            assert request.source_ids == [source_id]
            assert request.mode == InferenceMode.EDITOR_INLINE

            assert chunks[0].state == StreamState.START
            deltas = [c for c in chunks if c.state == StreamState.DELTA]
            assert deltas[0].content == "ok"
            assert chunks[-1].state == StreamState.END

        asyncio.run(run())

    def test_uses_folder_assistant_prompt_when_set(self) -> None:
        async def run() -> None:
            user_id = uuid4()
            folder_id = uuid4()
            assistant_id = uuid4()
            folder = make_folder(
                folder_id=folder_id, owner_id=user_id, assistant_id=assistant_id
            )

            folder_repository = AsyncMock(
                spec=IFolderRepository,
                get_by_id=AsyncMock(return_value=folder),
            )
            mock_assistant = Mock()
            mock_assistant.instructions.prompt = "Folder prompt"
            assistant_repository = AsyncMock()
            assistant_repository.get_by_id = AsyncMock(return_value=mock_assistant)
            inference_engine = Mock(spec=IInferenceEngine)
            inference_engine.send.return_value = _mock_stream()

            use_case = StreamFolderEditorInlineUseCase(
                folder_repository=folder_repository,
                access_policy=Mock(spec=IFolderAccessPolicy),
                assistant_repository=assistant_repository,
                inference_engine=inference_engine,
            )

            async for _ in use_case.execute(
                StreamFolderEditorInlineCommand(
                    user_id=user_id,
                    folder_id=folder_id,
                    instruction="x",
                    document_markdown="y",
                )
            ):
                pass

            request = inference_engine.send.call_args[0][0]
            assert request.system_prompt == "Folder prompt"

        asyncio.run(run())

    def test_raises_when_access_denied(self) -> None:
        async def run() -> None:
            user_id = uuid4()
            folder_id = uuid4()
            folder = make_folder(folder_id=folder_id, owner_id=user_id)
            folder_repository = AsyncMock(
                spec=IFolderRepository,
                get_by_id=AsyncMock(return_value=folder),
            )
            access_policy = Mock(spec=IFolderAccessPolicy)
            access_policy.assert_is_allowed.side_effect = AccessPolicyError(
                folder.id, "denied"
            )
            inference_engine = Mock(spec=IInferenceEngine)

            use_case = StreamFolderEditorInlineUseCase(
                folder_repository=folder_repository,
                access_policy=access_policy,
                assistant_repository=AsyncMock(),
                inference_engine=inference_engine,
            )

            with pytest.raises(AccessPolicyError):
                async for _ in use_case.execute(
                    StreamFolderEditorInlineCommand(
                        user_id=user_id,
                        folder_id=folder_id,
                        instruction="x",
                        document_markdown="y",
                    )
                ):
                    pass

            inference_engine.send.assert_not_called()

        asyncio.run(run())


class TestStreamFolderEditorAutocompleteUseCase:
    def test_streams_and_builds_inference_request(self) -> None:
        async def run() -> None:
            user_id = uuid4()
            folder_id = uuid4()
            source_id = uuid4()
            folder = make_folder(folder_id=folder_id, owner_id=user_id)
            folder.add_source(SourceId(source_id))

            folder_repository = AsyncMock(
                spec=IFolderRepository,
                get_by_id=AsyncMock(return_value=folder),
            )
            access_policy = Mock(spec=IFolderAccessPolicy)
            assistant_repository = AsyncMock()
            inference_engine = Mock(spec=IInferenceEngine)
            inference_engine.send.return_value = _mock_stream("next")

            use_case = StreamFolderEditorAutocompleteUseCase(
                folder_repository=folder_repository,
                access_policy=access_policy,
                assistant_repository=assistant_repository,
                inference_engine=inference_engine,
            )

            command = StreamFolderEditorAutocompleteCommand(
                user_id=user_id,
                folder_id=folder_id,
                text_before_cursor="## He",
                text_after_cursor="llo",
            )
            chunks = [c async for c in use_case.execute(command)]

            inference_engine.send.assert_called_once()
            request = inference_engine.send.call_args[0][0]
            assert isinstance(request, InferenceRequestDTO)
            assert request.history == ()
            assert request.editor_content is None
            assert "## He" in request.query
            assert "llo" in request.query
            assert request.source_ids == [source_id]
            assert request.mode == InferenceMode.EDITOR_AUTOCOMPLETE
            assert "<cursor_completion_request>" in request.query

            deltas = [c for c in chunks if c.state == StreamState.DELTA]
            assert deltas[0].content == "next"

        asyncio.run(run())
