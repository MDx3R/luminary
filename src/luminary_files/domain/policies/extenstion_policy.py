import fnmatch
from collections.abc import Iterable

from luminary_files.domain.interfaces.extenstion_policy import (
    IMIMEPolicy,
)


class MIMEWhitelistPolicy(IMIMEPolicy):
    def __init__(self, allowed: Iterable[str]) -> None:
        self._allowed = {ext.lower() for ext in allowed}

    def is_allowed(self, mime_type: str) -> bool:
        return mime_type.lower() in self._allowed


class MIMEBlacklistPolicy(IMIMEPolicy):
    def __init__(self, forbidden_patterns: Iterable[str]) -> None:
        self._forbidden = {p.lower() for p in forbidden_patterns}

        self._wildcards = {p for p in self._forbidden if "*" in p}
        self._exact_matches = self._forbidden - self._wildcards

    def is_allowed(self, mime_type: str) -> bool:
        if not mime_type:
            return False

        mime_type = mime_type.lower().strip()

        if mime_type in self._exact_matches:
            return False

        for mask in self._wildcards:
            if fnmatch.fnmatch(mime_type, mask):
                return False

        return True
