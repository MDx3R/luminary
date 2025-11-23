from typing import BinaryIO

from langchain_community.document_loaders.unstructured import UnstructuredFileIOLoader
from llama_index.readers.file.unstructured import UnstructuredReader

from luminary.content.application.interfaces.services.content_extractor import (
    IFileContentExtractor,
)


class UnstructuredFileContentExtractor(IFileContentExtractor):
    async def extract(self, data: BinaryIO) -> bytes:
        loader = UnstructuredFileIOLoader(file=data)
        docs = await loader.aload()

        all_text_parts: list[str] = []
        for doc in docs:
            content = doc.page_content.strip()
            if not content:
                continue

            all_text_parts.append(content)

        full_text = "\n\n".join(all_text_parts)

        return full_text.encode("utf-8")


class LlamaIndexFileContentExtractor(IFileContentExtractor):
    def __init__(self, reader: UnstructuredReader) -> None:  # type: ignore[no-any-unimported]
        self.reader = reader

    async def extract(self, data: BinaryIO) -> bytes:
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
