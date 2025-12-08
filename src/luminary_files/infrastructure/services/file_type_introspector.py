from typing import BinaryIO

import filetype
from filetype.types import Type
from luminary_files.application.dtos.dtos import FileType
from luminary_files.application.exceptions import InvalidFileTypeError
from luminary_files.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)


class FileTypeIntrospector(IFileTypeIntrospector):
    def extract(self, data: BinaryIO) -> FileType:
        head = data.read(261)
        data.seek(0)
        kind: Type | None = filetype.guess(head)  # type: ignore
        if kind is None:
            raise InvalidFileTypeError

        return FileType(
            extension=kind.extension,  # pyright: ignore[reportUnknownArgumentType]
            mime=kind.mime,  # pyright: ignore[reportUnknownArgumentType]
        )
