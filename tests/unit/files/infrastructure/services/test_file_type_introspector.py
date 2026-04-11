from io import BytesIO

import pytest
from luminary_files.application.dtos.dtos import FileType
from luminary_files.infrastructure.services.file_type_introspector import (
    FileTypeIntrospector,
)


class TestFileTypeIntrospector:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file_type_introspector = FileTypeIntrospector()
        # JPEG magic number (simplified header for testing)
        self.jpeg_content = BytesIO(
            b"\xff\xd8\xff\xe0" + b"\x00" * 257  # 261 bytes total
        )
        # PNG magic number
        self.png_content = BytesIO(
            b"\x89PNG\x0d\x0a\x1a\x0a" + b"\x00" * 253  # 261 bytes total
        )
        # Invalid content (non-recognizable file type)
        self.invalid_content = BytesIO(
            b"invalid_data" + b"\x00" * 250
        )  # 261 bytes total

    def test_extract_jpeg_success(self):
        # Act
        result = self.file_type_introspector.extract(self.jpeg_content)

        # Assert
        assert isinstance(result, FileType)
        assert result.extension == "jpg"
        assert result.mime == "image/jpeg"
        assert self.jpeg_content.tell() == 0  # Stream position reset

    def test_extract_png_success(self):
        # Act
        result = self.file_type_introspector.extract(self.png_content)

        # Assert
        assert isinstance(result, FileType)
        assert result.extension == "png"
        assert result.mime == "image/png"
        assert self.png_content.tell() == 0  # Stream position reset

    def test_extract_invalid_file_type_returns_txt(self):
        # Act
        result = self.file_type_introspector.extract(self.invalid_content)

        # Assert
        assert isinstance(result, FileType)
        assert result.extension == "txt"
        assert result.mime == "text/plain"
        assert self.invalid_content.tell() == 0  # Stream position reset
