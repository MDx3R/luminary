import mimetypes
from typing import BinaryIO

import filetype
from filetype.types import Type
from luminary_files.application.dtos.dtos import FileType
from luminary_files.application.exceptions import InvalidFileTypeError
from luminary_files.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)
from magika import Magika


class FileTypeIntrospector(IFileTypeIntrospector):
    def extract(self, data: BinaryIO) -> FileType:
        head = data.read(261)
        data.seek(0)
        kind: Type | None = filetype.guess(head)  # type: ignore

        if kind is not None:
            return FileType(extension=kind.extension, mime=kind.mime)

        try:
            head.decode("utf-8")
            return FileType(extension="txt", mime="text/plain")
        except UnicodeDecodeError as exc:
            raise InvalidFileTypeError() from exc


class MagikaFileTypeIntrospector(IFileTypeIntrospector):
    def __init__(self) -> None:
        self.magika = Magika()

    def extract(self, data: BinaryIO) -> FileType:
        data.seek(0)
        prediction = self.magika.identify_bytes(data.read())
        data.seek(0)

        real_mime = prediction.output.mime_type
        extension = mimetypes.guess_extension(real_mime) or ".txt"

        return FileType(extension=extension.rstrip("."), mime=real_mime)
