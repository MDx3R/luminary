from luminary.model.application.interfaces.services.engine import InferenceMode
from luminary.model.application.prompts.templates import (
    USER_MESSAGE_AUTOCOMPLETE_CURSOR,
    USER_MESSAGE_CHAT_OR_INLINE,
)


def _editor_section(editor_content: str | None) -> str:
    if not editor_content or not editor_content.strip():
        return ""
    body = editor_content.strip()
    return f"<editor_draft>\n{body}\n</editor_draft>\n"


def _retrieved_section(rag_context_str: str | None) -> str:
    if not rag_context_str or not rag_context_str.strip():
        return ""
    body = rag_context_str.strip()
    return f"<retrieved_context>\n{body}\n</retrieved_context>\n"


def build_user_request_content(
    query: str,
    editor_content: str | None,
    rag_context_str: str | None,
    *,
    mode: InferenceMode,
) -> str:
    """Build the user message for chat and editor-inline modes."""
    if mode == InferenceMode.EDITOR_AUTOCOMPLETE:
        return query

    return USER_MESSAGE_CHAT_OR_INLINE.format(
        editor_section=_editor_section(editor_content),
        retrieved_section=_retrieved_section(rag_context_str),
        query=query.strip(),
    )


def build_autocomplete_user_content(text_before: str, text_after: str) -> str:
    """Minimal volatile user turn for autocomplete; mode rules live in the system prompt."""
    return USER_MESSAGE_AUTOCOMPLETE_CURSOR.format(
        text_before=text_before,
        text_after=text_after,
    )
