from abc import ABC, abstractmethod

from luminary.assistant.domain.entity.assisnant import Assistant
from luminary.chat.domain.entity.chat import Chat


class IAssistantService(ABC):
    @abstractmethod
    def apply_assistant_instructions_to_chat(
        self, assistant: Assistant, chat: Chat
    ) -> None: ...
