"""Per-mode instruction blocks appended after the base identity.

Separated from the base prompt so mode-specific behavior stays stable and cache-friendly.
"""

from typing import Final

from luminary.model.application.interfaces.services.engine import (
    ChatSourceContext,
    InferenceMode,
)


__all__ = ["MODE_CHAT_FOLDER", "MODE_CHAT_STANDALONE", "resolve_mode_instructions"]

MODE_CHAT_FOLDER: Final[str] = """## Current task mode: Folder chat (full agent context)
- You may use conversation history, retrieved sources attached to this folder and this chat, and the folder editor draft when provided.
- Folder-level sources are shared workspace knowledge; chat-level sources are attached specifically to this thread—combine them when both are relevant.
- Aim answers at improving the user's understanding and their editor document: actionable synthesis, not generic essays."""

MODE_CHAT_STANDALONE: Final[str] = """## Current task mode: Standalone chat
- This chat is not inside a folder workflow. Only sources explicitly attached to this chat apply—do not assume folder-wide knowledge exists.
- If the user asks for grounded answers without attached sources, rely on general reasoning and clearly separate speculation from facts."""

MODE_EDITOR_INLINE: Final[str] = """## Current task mode: Editor inline command
- There is no chat history—only the user's instruction and the current document snapshot (when provided).
- Execute focused edits or transformations the user asked for: tighten prose, restructure, summarize a selection, fix Markdown, etc.
- Prefer minimal diffs in spirit: change only what the instruction implies unless the user asks for a full rewrite.
- Output should be directly usable in the editor (plain Markdown unless the user specifies another format)."""

MODE_EDITOR_AUTOCOMPLETE: Final[
    str
] = """## Current task mode: Markdown autocomplete at cursor
- You complete text at the cursor inside an existing Markdown document. The user message contains only `<text_before_cursor>` and `<text_after_cursor>` buffers.
- Emit only the characters to insert at the cursor—continuation of the current line, word, list item, heading, or fenced code block as appropriate.
- Do not repeat any characters from `text_before_cursor` or `text_after_cursor`. Do not wrap output in quotes or markdown fences unless completing inside an already-open fence.
- Stay syntactically consistent with surrounding Markdown (heading levels, list markers, indentation).
- Keep completions concise; avoid explanations, meta-commentary, or XML tags in the output."""


def resolve_mode_instructions(
    mode: InferenceMode,
    chat_source_context: ChatSourceContext | None,
) -> str:
    if mode == InferenceMode.CHAT:
        if chat_source_context == ChatSourceContext.FOLDER:
            return MODE_CHAT_FOLDER
        return MODE_CHAT_STANDALONE
    if mode == InferenceMode.EDITOR_INLINE:
        return MODE_EDITOR_INLINE
    return MODE_EDITOR_AUTOCOMPLETE
