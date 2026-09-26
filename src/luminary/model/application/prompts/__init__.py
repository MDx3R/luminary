from luminary.model.application.prompts.defaults import (
    DEFAULT_ASSISTANT_INSTRUCTIONS_ON_CREATE,
    EMPTY_ASSISTANT_INSTRUCTIONS,
)
from luminary.model.application.prompts.luminary_identity import (
    LUMINARY_BASE_SYSTEM_PROMPT,
)
from luminary.model.application.prompts.streaming_signals import (
    AUTOCOMPLETE_EMPTY_SIGNAL,
)
from luminary.model.application.prompts.system_message import (
    build_system_message,
    compose_instruction_body,
    render_final_system_prompt,
)
from luminary.model.application.prompts.templates import (
    INSTRUCTION_BODY_ASSISTANT_SUFFIX,
    SYSTEM_PROMPT_WITH_INSTRUCTIONS,
    USER_MESSAGE_AUTOCOMPLETE_CURSOR,
    USER_MESSAGE_CHAT_OR_INLINE,
)
from luminary.model.application.prompts.user_message_format import (
    build_autocomplete_user_content,
    build_user_request_content,
)


__all__ = [
    "AUTOCOMPLETE_EMPTY_SIGNAL",
    "DEFAULT_ASSISTANT_INSTRUCTIONS_ON_CREATE",
    "EMPTY_ASSISTANT_INSTRUCTIONS",
    "INSTRUCTION_BODY_ASSISTANT_SUFFIX",
    "LUMINARY_BASE_SYSTEM_PROMPT",
    "SYSTEM_PROMPT_WITH_INSTRUCTIONS",
    "USER_MESSAGE_AUTOCOMPLETE_CURSOR",
    "USER_MESSAGE_CHAT_OR_INLINE",
    "build_autocomplete_user_content",
    "build_system_message",
    "build_user_request_content",
    "compose_instruction_body",
    "render_final_system_prompt",
]
