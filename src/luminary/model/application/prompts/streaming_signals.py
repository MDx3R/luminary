"""Stable protocol strings for streamed inference (prompts + HTTP clients).

Autocomplete streams use `AUTOCOMPLETE_EMPTY_SIGNAL` when nothing should be inserted.
"""

AUTOCOMPLETE_EMPTY_SIGNAL: str = "__LUMINARY_AUTOCOMPLETE_EMPTY__"
