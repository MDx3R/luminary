from enum import Enum


class Author(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
