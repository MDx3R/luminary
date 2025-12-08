from enum import Enum


class SourceType(str, Enum):
    FILE = "file"
    LINK = "link"
    PAGE = "page"


class FetchStatus(str, Enum):
    NOT_FETCHED = "not_fetched"
    FETCHED = "fetched"
    EMBEDDED = "embedded"
    FAILED = "failed"
