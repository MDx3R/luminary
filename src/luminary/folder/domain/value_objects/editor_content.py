from dataclasses import dataclass

from common.domain.value_objects.datetime import DateTime


@dataclass(frozen=True)
class EditorContent:
    text: str
    updated_at: DateTime
