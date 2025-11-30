from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from luminary_files.application.interfaces.services.file_service import IFileService
from luminary_files.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetFilePresignedUrlUseCase,
)


class GetFilePresignedUrlUseCase(IGetFilePresignedUrlUseCase):
    def __init__(self, file_service: IFileService) -> None:
        self.file_service = file_service

    async def execute(self, query: GetPresignedUrlQuery) -> str:
        return await self.file_service.get_file_presigned_url(query)
