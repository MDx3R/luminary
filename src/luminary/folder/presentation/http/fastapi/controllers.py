from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.cbv import cbv
from fastapi import APIRouter, Depends, status
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import get_descriptor

from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import (
    AddSourceToFolderCommand,
    IAddSourceToFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.change_folder_assistant_use_case import (
    ChangeFolderAssistantCommand,
    IChangeFolderAssistantUseCase,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_chat_use_case import (
    CreateFolderChatCommand,
    ICreateFolderChatUseCase,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_use_case import (
    CreateFolderCommand,
    ICreateFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.delete_folder_use_case import (
    DeleteFolderCommand,
    IDeleteFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.remove_chat_from_folder_use_case import (
    IRemoveChatFromFolderUseCase,
    RemoveChatFromFolderCommand,
)
from luminary.folder.application.interfaces.usecases.command.remove_folder_assistant_use_case import (
    IRemoveFolderAssistantUseCase,
    RemoveFolderAssistantCommand,
)
from luminary.folder.application.interfaces.usecases.command.remove_source_from_folder_use_case import (
    IRemoveSourceFromFolderUseCase,
    RemoveSourceFromFolderCommand,
)
from luminary.folder.application.interfaces.usecases.command.update_editor_content_use_case import (
    IUpdateEditorContentUseCase,
    UpdateEditorContentCommand,
)
from luminary.folder.application.interfaces.usecases.command.update_folder_info_use_case import (
    IUpdateFolderInfoUseCase,
    UpdateFolderInfoCommand,
)
from luminary.folder.application.interfaces.usecases.query.get_folder_use_case import (
    GetFolderByIdQuery,
    IGetFolderByIdUseCase,
)
from luminary.folder.application.interfaces.usecases.query.list_user_folders_use_case import (
    IListUserFoldersUseCase,
    ListUserFoldersQuery,
)
from luminary.folder.presentation.http.dto.request import (
    AddSourceToFolderRequest,
    ChangeFolderAssistantRequest,
    CreateFolderChatRequest,
    CreateFolderRequest,
    UpdateEditorContentRequest,
    UpdateFolderInfoRequest,
)
from luminary.folder.presentation.http.dto.response import (
    FolderResponse,
    FolderSummaryResponse,
)


command_router = APIRouter()


@cbv(command_router)
class FolderCommandController:
    create_folder_use_case: ICreateFolderUseCase = Depends()
    update_folder_info_use_case: IUpdateFolderInfoUseCase = Depends()
    delete_folder_use_case: IDeleteFolderUseCase = Depends()
    change_folder_assistant_use_case: IChangeFolderAssistantUseCase = Depends()
    remove_folder_assistant_use_case: IRemoveFolderAssistantUseCase = Depends()
    add_source_to_folder_use_case: IAddSourceToFolderUseCase = Depends()
    remove_source_from_folder_use_case: IRemoveSourceFromFolderUseCase = Depends()
    create_folder_chat_use_case: ICreateFolderChatUseCase = Depends()
    remove_chat_from_folder_use_case: IRemoveChatFromFolderUseCase = Depends()
    update_editor_content_use_case: IUpdateEditorContentUseCase = Depends()

    @command_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
        self,
        request: CreateFolderRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        folder_id = await self.create_folder_use_case.execute(
            CreateFolderCommand(
                user_id=descriptor.identity_id,
                name=request.name,
                description=request.description,
                assistant_id=request.assistant_id,
            )
        )
        return IDResponse(id=folder_id)

    @command_router.put(
        "/{folder_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update_info(
        self,
        folder_id: UUID,
        request: UpdateFolderInfoRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_folder_info_use_case.execute(
            UpdateFolderInfoCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                name=request.name,
                description=request.description,
            )
        )

    @command_router.delete(
        "/{folder_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete(
        self,
        folder_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.delete_folder_use_case.execute(
            DeleteFolderCommand(user_id=descriptor.identity_id, folder_id=folder_id)
        )

    @command_router.put(
        "/{folder_id:uuid}/assistant",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def change_assistant(
        self,
        folder_id: UUID,
        request: ChangeFolderAssistantRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.change_folder_assistant_use_case.execute(
            ChangeFolderAssistantCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                assistant_id=request.assistant_id,
            )
        )

    @command_router.delete(
        "/{folder_id:uuid}/assistant",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def remove_assistant(
        self,
        folder_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.remove_folder_assistant_use_case.execute(
            RemoveFolderAssistantCommand(
                user_id=descriptor.identity_id, folder_id=folder_id
            )
        )

    @command_router.post(
        "/{folder_id:uuid}/sources",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def add_source(
        self,
        folder_id: UUID,
        request: AddSourceToFolderRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.add_source_to_folder_use_case.execute(
            AddSourceToFolderCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                source_id=request.source_id,
            )
        )

    @command_router.delete(
        "/{folder_id:uuid}/sources/{source_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def remove_source(
        self,
        folder_id: UUID,
        source_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.remove_source_from_folder_use_case.execute(
            RemoveSourceFromFolderCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                source_id=source_id,
            )
        )

    @command_router.post("/{folder_id:uuid}/chats", status_code=status.HTTP_201_CREATED)
    async def create_chat(
        self,
        folder_id: UUID,
        request: CreateFolderChatRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        chat_id = await self.create_folder_chat_use_case.execute(
            CreateFolderChatCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                name=request.name,
                assistant_id=request.assistant_id,
                model_id=request.model_id,
                max_context_messages=request.max_context_messages,
            )
        )
        return IDResponse(id=chat_id)

    @command_router.delete(
        "/{folder_id:uuid}/chats/{chat_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def remove_chat(
        self,
        folder_id: UUID,
        chat_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.remove_chat_from_folder_use_case.execute(
            RemoveChatFromFolderCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                chat_id=chat_id,
            )
        )

    @command_router.put(
        "/{folder_id:uuid}/editor",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update_editor(
        self,
        folder_id: UUID,
        request: UpdateEditorContentRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_editor_content_use_case.execute(
            UpdateEditorContentCommand(
                user_id=descriptor.identity_id,
                folder_id=folder_id,
                text=request.text,
            )
        )


query_router = APIRouter()


@cbv(query_router)
class FolderQueryController:
    get_folder_by_id_use_case: IGetFolderByIdUseCase = Depends()
    list_user_folders_use_case: IListUserFoldersUseCase = Depends()

    @query_router.get("/")
    async def list_folders(
        self,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> list[FolderSummaryResponse]:
        read_models = await self.list_user_folders_use_case.execute(
            ListUserFoldersQuery(user_id=descriptor.identity_id)
        )
        return [FolderSummaryResponse.from_read_model(m) for m in read_models]

    @query_router.get("/{folder_id:uuid}")
    async def get_folder(
        self,
        folder_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> FolderResponse:
        read_model = await self.get_folder_by_id_use_case.execute(
            GetFolderByIdQuery(user_id=descriptor.identity_id, folder_id=folder_id)
        )
        return FolderResponse.from_read_model(read_model)
