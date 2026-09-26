"""Compose full system prompt from base identity, mode, and optional assistant slice."""

from luminary.model.application.interfaces.services.engine import (
    ChatSourceContext,
    InferenceMode,
    InferenceRequestDTO,
)
from luminary.model.application.prompts.mode_instructions import (
    resolve_mode_instructions,
)
from luminary.model.application.prompts.templates import (
    INSTRUCTION_BODY_ASSISTANT_SUFFIX,
    SYSTEM_PROMPT_WITH_INSTRUCTIONS,
)


def compose_instruction_body(
    mode: InferenceMode,
    chat_source_context: ChatSourceContext | None,
    assistant_instructions: str,
) -> str:
    """Merge mode block and optional assistant-specific instructions from DB or defaults."""
    mode_text = resolve_mode_instructions(mode, chat_source_context).strip()
    stripped_assistant = assistant_instructions.strip()
    parts: list[str] = []
    if mode_text:
        parts.append(mode_text)
    if stripped_assistant:
        parts.append(
            INSTRUCTION_BODY_ASSISTANT_SUFFIX.format(
                assistant_instructions=stripped_assistant,
            )
        )
    return "\n\n".join(parts)


def build_system_message(base_system_prompt: str, instruction_body: str) -> str:
    """Combine base Luminary identity with merged mode and assistant sections."""
    if not instruction_body.strip():
        return base_system_prompt

    return SYSTEM_PROMPT_WITH_INSTRUCTIONS.format(
        base_identity=base_system_prompt,
        instruction_body=instruction_body.strip(),
    )


def render_final_system_prompt(
    base_system_prompt: str,
    request: InferenceRequestDTO,
) -> str:
    """Full system string for an inference request (identity + mode + assistant)."""
    ctx = request.chat_source_context if request.mode == InferenceMode.CHAT else None
    instruction_body = compose_instruction_body(
        request.mode,
        ctx,
        request.system_prompt,
    )
    return build_system_message(base_system_prompt, instruction_body)
