from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.value_objects.datetime import DateTime
from tests.unit.assistant.utils import make_assistant, make_instructions

from luminary.assistant.domain.services.assistant_service import AssistantService
from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings


class TestAssistantService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.service = AssistantService()

    def test_apply_assistant_instructions_to_chat(self) -> None:
        assistant = make_assistant(
            instructions=make_instructions(prompt="This is assistant prompt")
        )
        chat = Chat(
            uuid4(),
            uuid4(),
            None,
            ChatInfo("Chat"),
            ChatSettings(uuid4(), "This is system prompt", 20),
            DateTime(datetime.now(UTC)),
        )

        self.service.apply_assistant_instructions_to_chat(assistant, chat)

        assert chat.settings.system_prompt == assistant.instructions.prompt
