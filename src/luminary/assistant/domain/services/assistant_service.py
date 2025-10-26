from common.domain.exceptions import InvariantViolationError

from luminary.assistant.domain.entity.assisnant import Assistant
from luminary.assistant.domain.interfaces.assistant_service import IAssistantService
from luminary.chat.domain.entity.chat import Chat


class AssistantService(IAssistantService):
    def apply_assistant_instructions_to_chat(
        self, assistant: Assistant, chat: Chat
    ) -> None:
        if assistant.instructions is None:
            raise InvariantViolationError(
                "Assistant must have specified instructions to apply them for chat"
            )

        chat.change_system_prompt(assistant.instructions.prompt)
