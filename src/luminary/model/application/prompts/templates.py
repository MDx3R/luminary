"""LlamaIndex PromptTemplate definitions for inspectable, stable prompt structure.

Templates are module-level singletons: use `.get_template()` for the raw pattern and
`.metadata` (including `luminary_prompt_id`) for tracing in logs or observability.
"""

from llama_index.core import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType


def _meta(prompt_id: str, description: str) -> dict[str, str]:
    return {
        "luminary_prompt_id": prompt_id,
        "description": description,
    }


# --- System: base identity + optional instruction stack (mode + assistant)
SYSTEM_PROMPT_WITH_INSTRUCTIONS = PromptTemplate(
    template=(
        "{base_identity}\n\n---\n\n{instruction_body}"
    ),
    prompt_type=PromptType.CUSTOM,
    metadata=_meta(
        "luminary.system.with_instructions",
        "Full Luminary system prompt when mode and/or assistant layers are present.",
    ),
)

# --- User turn: chat & editor-inline (not autocomplete)
USER_MESSAGE_CHAT_OR_INLINE = PromptTemplate(
    template=(
        "<user_message>\n"
        "<instructions>\n"
        "Answer using retrieved context when it helps. If context is empty or "
        "irrelevant, rely on the query and editor draft alone.\n"
        "</instructions>\n"
        "{editor_section}"
        "{retrieved_section}"
        "<user_query>\n"
        "{query}\n"
        "</user_query>\n"
        "</user_message>"
    ),
    prompt_type=PromptType.CUSTOM,
    metadata=_meta(
        "luminary.user.chat_or_inline",
        "Structured user message for CHAT and EDITOR_INLINE modes.",
    ),
)

# --- User turn: autocomplete cursor buffers only
USER_MESSAGE_AUTOCOMPLETE_CURSOR = PromptTemplate(
    template=(
        "<cursor_completion_request>\n"
        "<text_before_cursor>\n"
        "{text_before}\n"
        "</text_before_cursor>\n"
        "<text_after_cursor>\n"
        "{text_after}\n"
        "</text_after_cursor>\n"
        "</cursor_completion_request>"
    ),
    prompt_type=PromptType.CUSTOM,
    metadata=_meta(
        "luminary.user.autocomplete_cursor",
        "Volatile cursor context for EDITOR_AUTOCOMPLETE; rules live in system prompt.",
    ),
)

# --- Instruction body: mode text + optional assistant label (composed upstream)
INSTRUCTION_BODY_ASSISTANT_SUFFIX = PromptTemplate(
    template="Assistant instructions:\n{assistant_instructions}",
    prompt_type=PromptType.CUSTOM,
    metadata=_meta(
        "luminary.instruction.assistant_suffix",
        "Labels DB-backed assistant instructions after mode block.",
    ),
)
