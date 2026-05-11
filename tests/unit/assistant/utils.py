from uuid import UUID, uuid4

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import (
    Assistant,
    AssistantId,
    AssistantInfo,
    Instructions,
)
from luminary.assistant.domain.enums import AssistantType


def make_instructions(
    *,
    prompt: str = "Test prompt",
) -> Instructions:
    return Instructions(prompt=prompt)


def make_assistant(  # noqa: PLR0913
    *,
    assistant_id: UUID | None = None,
    user_id: UUID | None = None,
    name: str = "Test Assistant",
    description: str = "Test Description",
    instructions: Instructions | None = None,
    type: AssistantType = AssistantType.PERSONAL,
    is_deleted: bool = False,
    tags: list[str] | None = None,
) -> Assistant:
    assistant_id = assistant_id or uuid4()
    # System assistants may omit owner; all others require one
    if type != AssistantType.SYSTEM:
        user_id = user_id or uuid4()
    owner = UserId(user_id) if user_id is not None else None
    return Assistant(
        id=AssistantId(assistant_id),
        owner_id=owner,
        type=type,
        info=AssistantInfo(name=name, description=description),
        instructions=instructions or make_instructions(),
        is_deleted=is_deleted,
        tags=tags if tags is not None else [],
    )
