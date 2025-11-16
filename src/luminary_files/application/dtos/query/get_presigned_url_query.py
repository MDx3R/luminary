from dataclasses import dataclass


@dataclass(frozen=True)
class GetPresignedUrlQuery:
    object_key: str
