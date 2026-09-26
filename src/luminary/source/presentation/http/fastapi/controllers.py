from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.cbv import cbv
from fastapi import APIRouter, Depends, Form, UploadFile, status
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import get_descriptor
from luminary_files.application.interfaces.services.file_service import (
    IFileService,
    UploadFileCommand,
)

from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateFileSourceCommand,
    CreateLinkSourceCommand,
    CreatePageSourceCommand,
    ICreateFileSourceUseCase,
    ICreateLinkSourceUseCase,
    ICreatePageSourceUseCase,
)
from luminary.source.application.interfaces.usecases.command.delete_source_use_case import (
    DeleteSourceCommand,
    IDeleteSourceUseCase,
)
from luminary.source.application.interfaces.usecases.command.update_source_use_case import (
    IUpdateSourceUseCase,
    UpdateSourceCommand,
)
from luminary.source.application.interfaces.usecases.query.get_source_use_case import (
    GetSourceByIdQuery,
    IGetSourceByIdUseCase,
)
from luminary.source.application.interfaces.usecases.query.list_user_sources_use_case import (
    IListUserSourcesUseCase,
    ListUserSourcesQuery,
)
from luminary.source.presentation.http.dto.request import (
    CreateLinkSourceRequest,
    CreatePageSourceRequest,
    UpdateSourceRequest,
)
from luminary.source.presentation.http.dto.response import SourceResponse


command_router = APIRouter()


@cbv(command_router)
class SourceCommandController:
    create_file_source_use_case: ICreateFileSourceUseCase = Depends()
    create_page_source_use_case: ICreatePageSourceUseCase = Depends()
    create_link_source_use_case: ICreateLinkSourceUseCase = Depends()
    update_source_use_case: IUpdateSourceUseCase = Depends()
    delete_source_use_case: IDeleteSourceUseCase = Depends()
    file_service: IFileService = Depends()

    @command_router.post("/file", dependencies=[], status_code=status.HTTP_201_CREATED)
    async def create_file(
        self,
        file: UploadFile,
        title: Annotated[str, Form()],
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        file_id = await self.file_service.upload_file(
            UploadFileCommand(
                user_id=descriptor.identity_id,
                filename=file.filename or "file",
                content=file.file,
            )
        )
        source_id = await self.create_file_source_use_case.execute(
            CreateFileSourceCommand(
                user_id=descriptor.identity_id, title=title, file_id=file_id
            )
        )

        return IDResponse(id=source_id)

    @command_router.post("/page", dependencies=[], status_code=status.HTTP_201_CREATED)
    async def create_page(
        self,
        page: UploadFile,
        request: CreatePageSourceRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        source_id = await self.create_page_source_use_case.execute(
            CreatePageSourceCommand(
                user_id=descriptor.identity_id, title=request.title, data=page.file
            )
        )

        return IDResponse(id=source_id)

    @command_router.post("/link", dependencies=[], status_code=status.HTTP_201_CREATED)
    async def create_link(
        self,
        request: CreateLinkSourceRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        source_id = await self.create_link_source_use_case.execute(
            CreateLinkSourceCommand(
                user_id=descriptor.identity_id, title=request.title, url=request.url
            )
        )

        return IDResponse(id=source_id)

    @command_router.put(
        "/{source_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update(
        self,
        source_id: UUID,
        request: UpdateSourceRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_source_use_case.execute(
            UpdateSourceCommand(
                user_id=descriptor.identity_id,
                source_id=source_id,
                title=request.title,
            )
        )

    @command_router.delete(
        "/{source_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete(
        self,
        source_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.delete_source_use_case.execute(
            DeleteSourceCommand(
                user_id=descriptor.identity_id,
                source_id=source_id,
            )
        )


query_router = APIRouter()


@cbv(query_router)
class SourceQueryController:
    get_source_by_id_use_case: IGetSourceByIdUseCase = Depends()
    list_user_sources_use_case: IListUserSourcesUseCase = Depends()

    @query_router.get("/")
    async def list_sources(
        self,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> list[SourceResponse]:
        read_models = await self.list_user_sources_use_case.execute(
            ListUserSourcesQuery(user_id=descriptor.identity_id)
        )
        return [SourceResponse.from_read_model(m) for m in read_models]

    @query_router.get("/{source_id:uuid}")
    async def get_source(
        self,
        source_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> SourceResponse:
        read_model = await self.get_source_by_id_use_case.execute(
            GetSourceByIdQuery(user_id=descriptor.identity_id, source_id=source_id)
        )
        return SourceResponse.from_read_model(read_model)
