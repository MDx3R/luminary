from dataclasses import dataclass


@dataclass(frozen=True)
class FileType:
    extension: str
    mime: str
