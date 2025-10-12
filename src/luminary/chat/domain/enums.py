from enum import Enum


class ChatMessageAuthor(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
