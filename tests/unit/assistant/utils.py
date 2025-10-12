from uuid import UUID, uuid4

from luminary.assistant.domain.entity.assisnant import Assistant, Instructions


# Factory function to create an Instructions instance
def make_instructions(
    *,
    prompt: str = "Test prompt",
) -> Instructions:
    """Create an Instructions instance with an optional prompt."""
    return Instructions(prompt=prompt)


# Factory function to create an Assistant instance
def make_assistant(
    *,
    assistant_id: UUID | None = None,
    user_id: UUID | None = None,
    name: str = "Test Assistant",
    description: str = "Test Description",
    instructions: Instructions | None = None,
) -> Assistant:
    """Create an Assistant instance with optional IDs, name, description, and instructions."""
    assistant_id = assistant_id or uuid4()
    user_id = user_id or uuid4()
    return Assistant(
        assistant_id=assistant_id,
        user_id=user_id,
        name=name,
        description=description,
        instructions=instructions,
    )
