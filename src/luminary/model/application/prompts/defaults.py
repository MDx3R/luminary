"""Default assistant instruction text when none is configured or when creating an assistant."""

from typing import Final


# Used when no assistant is bound; omit the "Assistant instructions" section entirely (see compose_instruction_body).
EMPTY_ASSISTANT_INSTRUCTIONS: Final[str] = ""

# Shown when the user creates an assistant without supplying custom instructions (stored in DB).
DEFAULT_ASSISTANT_INSTRUCTIONS_ON_CREATE: Final[str] = """
You follow Luminary's co-pilot defaults: support the user's writing and analysis, ground answers in attached sources when present, and keep the user's voice primary.
Prefer structured responses when helpful (short headings, bullets). Offer alternatives rather than a single imposed answer unless the user asks for one definitive version."""
