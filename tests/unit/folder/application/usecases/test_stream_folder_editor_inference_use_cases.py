from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
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
from luminary.model.application.prompts import AUTOCOMPLETE_EMPTY_SIGNAL
from luminary.source.domain.entity.source import SourceId


async def _mock_stream(*chunks: str) -> AsyncGenerator[EngineStreamingResponse]:
    for c in chunks:
        yield EngineStreamingResponse(content=c)


async def _mock_empty_stream() -> AsyncGenerator[EngineStreamingResponse, None]:
    while False:
        yield EngineStreamingResponse(content="")


async def _mock_whitespace_only_stream() -> AsyncGenerator[EngineStreamingResponse]:
    yield EngineStreamingResponse(content="  \n\t")


@pytest.mark.asyncio
class TestStreamFolderEditorInlineUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.folder_id = uuid4()
        self.folder = make_folder(folder_id=self.folder_id, owner_id=self.user_id)

        self.folder_repository = Mock(
            spec=IFolderRepository,
            get_by_id=AsyncMock(return_value=self.folder),
        )
        self.access_policy = Mock(spec=IFolderAccessPolicy)
        self.assistant_repository = Mock(spec=IAssistantRepository)
        self.inference_engine = Mock(
            spec=IInferenceEngine, send=Mock(return_value=_mock_stream("ok"))
        )

        self.use_case = StreamFolderEditorInlineUseCase(
            folder_repository=self.folder_repository,
            access_policy=self.access_policy,
            assistant_repository=self.assistant_repository,
            inference_engine=self.inference_engine,
        )

    async def test_streams_and_builds_inference_request(self) -> None:
        # Arrange
        source_id = uuid4()
        self.folder.add_source(SourceId(source_id))
        command = StreamFolderEditorInlineCommand(
            user_id=self.user_id,
            folder_id=self.folder_id,
            instruction="Shorten intro",
            document_markdown="# Doc",
        )

        # Act
        chunks = [c async for c in self.use_case.execute(command)]

        # Assert
        self.folder_repository.get_by_id.assert_awaited_once_with(
            FolderId(self.folder_id)
        )
        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.folder
        )
        self.inference_engine.send.assert_called_once()
        request = self.inference_engine.send.call_args[0][0]
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

    async def test_uses_folder_assistant_prompt_when_set(self) -> None:
        # Arrange
        assistant_id = uuid4()
        self.folder = make_folder(
            folder_id=self.folder_id,
            owner_id=self.user_id,
            assistant_id=assistant_id,
        )
        self.folder_repository.get_by_id = AsyncMock(return_value=self.folder)
        mock_assistant = Mock()
        mock_assistant.instructions.prompt = "Folder prompt"
        self.assistant_repository.get_by_id = AsyncMock(return_value=mock_assistant)
        self.inference_engine.send.return_value = _mock_stream()

        # Act
        async for _ in self.use_case.execute(
            StreamFolderEditorInlineCommand(
                user_id=self.user_id,
                folder_id=self.folder_id,
                instruction="x",
                document_markdown="y",
            )
        ):
            pass

        # Assert
        request = self.inference_engine.send.call_args[0][0]
        assert request.system_prompt == "Folder prompt"

    async def test_raises_when_access_denied(self) -> None:
        # Arrange
        self.access_policy.assert_is_allowed.side_effect = AccessPolicyError(
            self.folder.id, "denied"
        )

        # Act
        with pytest.raises(AccessPolicyError):
            async for _ in self.use_case.execute(
                StreamFolderEditorInlineCommand(
                    user_id=self.user_id,
                    folder_id=self.folder_id,
                    instruction="x",
                    document_markdown="y",
                )
            ):
                pass

        # Assert
        self.inference_engine.send.assert_not_called()


@pytest.mark.asyncio
class TestStreamFolderEditorAutocompleteUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.folder_id = uuid4()
        self.folder = make_folder(folder_id=self.folder_id, owner_id=self.user_id)

        self.folder_repository = Mock(
            spec=IFolderRepository,
            get_by_id=AsyncMock(return_value=self.folder),
        )
        self.access_policy = Mock(spec=IFolderAccessPolicy)
        self.assistant_repository = Mock(spec=IAssistantRepository)
        self.inference_engine = Mock(
            spec=IInferenceEngine, send=Mock(return_value=_mock_stream("next"))
        )

        self.use_case = StreamFolderEditorAutocompleteUseCase(
            folder_repository=self.folder_repository,
            access_policy=self.access_policy,
            assistant_repository=self.assistant_repository,
            inference_engine=self.inference_engine,
        )

    async def test_streams_and_builds_inference_request(self) -> None:
        # Arrange
        source_id = uuid4()
        self.folder.add_source(SourceId(source_id))
        command = StreamFolderEditorAutocompleteCommand(
            user_id=self.user_id,
            folder_id=self.folder_id,
            text_before_cursor="## He",
            text_after_cursor="llo",
        )

        # Act
        chunks = [c async for c in self.use_case.execute(command)]

        # Assert
        self.inference_engine.send.assert_called_once()
        request = self.inference_engine.send.call_args[0][0]
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

    async def test_empty_model_output_emits_explicit_signal_and_end(self) -> None:
        # Arrange
        self.inference_engine.send.return_value = _mock_empty_stream()

        # Act
        chunks = [
            c
            async for c in self.use_case.execute(
                StreamFolderEditorAutocompleteCommand(
                    user_id=self.user_id,
                    folder_id=self.folder_id,
                    text_before_cursor="x",
                    text_after_cursor="",
                )
            )
        ]

        # Assert
        assert chunks[0].state == StreamState.START
        assert chunks[-1].state == StreamState.END
        deltas = [c for c in chunks if c.state == StreamState.DELTA]
        assert len(deltas) == 1
        assert deltas[0].content == AUTOCOMPLETE_EMPTY_SIGNAL

    async def test_whitespace_only_output_emits_explicit_signal(self) -> None:
        # Arrange
        self.inference_engine.send.return_value = _mock_whitespace_only_stream()

        # Act
        chunks = [
            c
            async for c in self.use_case.execute(
                StreamFolderEditorAutocompleteCommand(
                    user_id=self.user_id,
                    folder_id=self.folder_id,
                    text_before_cursor="",
                    text_after_cursor="",
                )
            )
        ]

        # Assert
        deltas = [c for c in chunks if c.state == StreamState.DELTA]
        assert len(deltas) == 1
        assert deltas[0].content == AUTOCOMPLETE_EMPTY_SIGNAL
