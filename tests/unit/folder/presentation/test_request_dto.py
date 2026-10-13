import pytest
from pydantic import ValidationError

from luminary.folder.presentation.http.dto.request import (
    StreamFolderEditorInlineRequest,
)


def test_inline_request_accepts_selected_text_and_instruction() -> None:
    request = StreamFolderEditorInlineRequest.model_validate(
        {
            "instruction": "Shorten this paragraph",
            "selected_text": "A paragraph selected in the editor.",
        }
    )

    assert request.instruction == "Shorten this paragraph"
    assert request.selected_text == "A paragraph selected in the editor."


def test_inline_request_requires_selected_text() -> None:
    with pytest.raises(ValidationError):
        StreamFolderEditorInlineRequest.model_validate(
            {
                "instruction": "Shorten this paragraph",
                "document_markdown": "The old full-document field.",
            }
        )
