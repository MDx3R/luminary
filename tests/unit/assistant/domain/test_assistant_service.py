import pytest
from tests.unit.assistant.utils import make_assistant, make_instructions
from tests.unit.chat.utils import make_chat

from luminary.assistant.domain.services.assistant_service import AssistantService


class TestAssistantService:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.service = AssistantService()

    def test_apply_assistant_instructions_to_chat(self) -> None:
        assistant = make_assistant(
            instructions=make_instructions(prompt="This is assistant prompt")
        )
        chat = make_chat()

        self.service.apply_assistant_instructions_to_chat(assistant, chat)

        assert chat.settings.system_prompt == assistant.instructions.prompt
