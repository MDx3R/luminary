from typing import BinaryIO

from llama_index.core.readers.base import BaseReader

from luminary.content.application.exceptions import ParsingError
from luminary.content.application.interfaces.services.content_extractor import (
    IFileContentExtractor,
)


class LlamaIndexFileContentExtractor(IFileContentExtractor):
    def __init__(self, reader: BaseReader) -> None:
        self.reader = reader

    async def extract(self, data: BinaryIO) -> bytes:
        try:
            docs = await self.reader.aload_data(
                unstructured_kwargs={"file": data, "metadata_filename": "file.txt"}
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
