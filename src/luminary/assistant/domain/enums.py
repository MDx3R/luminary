from enum import Enum


class AssistantType(str, Enum):
    """Type of assistant per project spec: Personal, System, Public."""

    PERSONAL = "personal"
    SYSTEM = "system"
    PUBLIC = "public"
