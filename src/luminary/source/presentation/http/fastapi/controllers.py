from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.auth import get_descriptor, require_authenticated
from fastapi import APIRouter, Depends, UploadFile
from fastapi_utils.cbv import cbv
from luminary_files.application.interfaces.services.file_service import (
    IFileService,
    UploadFileCommand,
)

from luminary.content.application.interfaces.services.content_service import (
    IContentService,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateFileSourceCommand,
    ICreateFileSourceUseCase,
)
from luminary.source.presentation.http.dto.request import CreateFileSourceRequest


command_router = APIRouter()


@cbv(command_router)
class SourceCommandController:
    create_file_source_use_case: ICreateFileSourceUseCase = Depends()
    file_service: IFileService = Depends()
    content_service: IContentService = Depends()

    @command_router.post("/", dependencies=[Depends(require_authenticated)])
    async def create_source(
        self,
        file: UploadFile,
        request: CreateFileSourceRequest,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> IDResponse:
        file_id = await self.file_service.upload_file(
            UploadFileCommand(
                user_id=descriptor, filename=file.filename or "file", content=file.file
            )
        )
        source_id = await self.create_file_source_use_case.execute(
            CreateFileSourceCommand(
                user_id=descriptor, title=request.title, file_id=file_id, data=file.file
            )
        )
        # done

        return IDResponse(id=source_id)
