from typing import BinaryIO

from langchain_community.document_loaders.unstructured import UnstructuredFileIOLoader

from luminary.content.application.interfaces.services.content_extractor import (
    IFileContentExtractor,
)


class UnstructuredFileContentExtractor(IFileContentExtractor):
    async def extract(self, data: BinaryIO) -> bytes:
        loader = UnstructuredFileIOLoader(file=data)
        docs = loader.load()

        all_text_parts: list[str] = []
        for doc in docs:
            content = doc.page_content.strip()
            if not content:
                continue

            all_text_parts.append(content)

        full_text = "\n\n".join(all_text_parts)

        return full_text.encode("utf-8")
