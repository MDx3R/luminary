from luminary.model.application.interfaces.services.engine import (
    ChatSourceContext,
    InferenceMode,
)
from luminary.model.application.prompts import (
    INSTRUCTION_BODY_ASSISTANT_SUFFIX,
    SYSTEM_PROMPT_WITH_INSTRUCTIONS,
    USER_MESSAGE_AUTOCOMPLETE_CURSOR,
    USER_MESSAGE_CHAT_OR_INLINE,
)
from luminary.model.application.prompts.system_message import (
    build_system_message,
    compose_instruction_body,
)
from luminary.model.application.prompts.user_message_format import (
    build_autocomplete_user_content,
    build_user_request_content,
)


def test_compose_instruction_body_includes_mode_and_assistant() -> None:
    body = compose_instruction_body(
        InferenceMode.CHAT,
        ChatSourceContext.FOLDER,
        "Be concise in lists.",
    )
    assert "Folder chat" in body
    assert "Assistant instructions" in body
    assert "Be concise" in body


def test_compose_instruction_body_omits_empty_assistant() -> None:
    body = compose_instruction_body(
        InferenceMode.EDITOR_INLINE,
        None,
        "",
    )
    assert "Assistant" not in body
    assert "Editor inline" in body


def test_build_system_message_skips_separator_when_no_body() -> None:
    out = build_system_message("BASE", "")
    assert out == "BASE"


def test_build_user_request_content_autocomplete_passthrough() -> None:
    ac = build_autocomplete_user_content("a", "b")
    out = build_user_request_content(
        ac,
        None,
        None,
        mode=InferenceMode.EDITOR_AUTOCOMPLETE,
    )
    assert out == ac
    assert "<text_before_cursor>" in out


def test_build_user_request_content_chat_includes_sections() -> None:
    out = build_user_request_content(
        "Why?",
        "# Title",
        "Context line",
        mode=InferenceMode.CHAT,
    )
    assert "<user_message>" in out
    assert "<editor_draft>" in out
    assert "# Title" in out
    assert "<retrieved_context>" in out
    assert "Context line" in out
    assert "<user_query>" in out
    assert "Why?" in out


def test_prompt_templates_have_trace_ids() -> None:
    for pt in (
        SYSTEM_PROMPT_WITH_INSTRUCTIONS,
        USER_MESSAGE_CHAT_OR_INLINE,
        USER_MESSAGE_AUTOCOMPLETE_CURSOR,
        INSTRUCTION_BODY_ASSISTANT_SUFFIX,
    ):
        assert "luminary_prompt_id" in pt.metadata
        assert pt.get_template().strip()
