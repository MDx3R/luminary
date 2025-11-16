from uuid import UUID, uuid4

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import (
    Assistant,
    AssistantId,
    AssistantInfo,
    Instructions,
)


# Factory function to create an Instructions instance
def make_instructions(
    *,
    prompt: str = "Test prompt",
) -> Instructions:
    """Create an Instructions instance with an optional prompt."""
    return Instructions(prompt=prompt)


# Factory function to create an Assistant instance
def make_assistant(  # noqa: PLR0913
    *,
    assistant_id: UUID | None = None,
    user_id: UUID | None = None,
    name: str = "Test Assistant",
    description: str = "Test Description",
    instructions: Instructions | None = None,
    is_deleted: bool = False,
) -> Assistant:
    """Create an Assistant instance with optional IDs, name, description, and instructions."""
    assistant_id = assistant_id or uuid4()
    user_id = user_id or uuid4()
    return Assistant(
        id=AssistantId(assistant_id),
        owner_id=UserId(user_id),
        info=AssistantInfo(name=name, description=description),
        instructions=instructions or make_instructions(),
        is_deleted=is_deleted,
    )
