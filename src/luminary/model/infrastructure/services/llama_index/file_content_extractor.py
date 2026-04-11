from typing import BinaryIO

from llama_index.core.readers.base import BaseReader
from luminary_files.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)

from luminary.content.application.exceptions import ParsingError
from luminary.content.application.interfaces.services.content_extractor import (
    IFileContentExtractor,
)


class LlamaIndexFileContentExtractor(IFileContentExtractor):
    def __init__(
        self, reader: BaseReader, file_introspector: IFileTypeIntrospector
    ) -> None:
        self.reader = reader
        self.file_introspector = file_introspector

    async def extract(self, filename: str, data: BinaryIO) -> bytes:
        file_type = self.file_introspector.extract(data)
        filename = f"{filename}.{file_type.extension}"

        try:
            docs = await self.reader.aload_data(
                unstructured_kwargs={"file": data, "metadata_filename": filename}
            )

            all_text_parts: list[str] = []
            for doc in docs:
                content = doc.get_content().strip()
                if not content:
                    continue

                all_text_parts.append(content)

            full_text = "\n\n".join(all_text_parts)

            return full_text.encode("utf-8")
        except Exception as exc:
            raise ParsingError() from exc
