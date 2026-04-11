from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.cbv import cbv
from fastapi import APIRouter, Depends, status
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import get_descriptor

from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
    ICreateAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.delete_assistant_use_case import (
    DeleteAssistantCommand,
    IDeleteAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_info_use_case import (
    IUpdateAssistantInfoUseCase,
    UpdateAssistantInfoCommand,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_instructions_use_case import (
    IUpdateAssistantInstructionsUseCase,
    UpdateAssistantInstructionsCommand,
)
from luminary.assistant.application.interfaces.usecases.query.get_assistant_use_case import (
    GetAssistantByIdQuery,
    IGetAssistantByIdUseCase,
)
from luminary.assistant.application.interfaces.usecases.query.list_assistants_use_case import (
    IListAssistantsUseCase,
    ListAssistantsQuery,
)
from luminary.assistant.presentation.http.dto.request import (
    CreateAssistantRequest,
    UpdateAssistantInfoRequest,
    UpdateAssistantInstructionsRequest,
)
from luminary.assistant.presentation.http.dto.response import (
    AssistantResponse,
    AssistantSummaryResponse,
)


command_router = APIRouter()


@cbv(command_router)
class AssistantCommandController:
    create_assistant_use_case: ICreateAssistantUseCase = Depends()
    update_assistant_info_use_case: IUpdateAssistantInfoUseCase = Depends()
    update_assistant_instructions_use_case: IUpdateAssistantInstructionsUseCase = (
        Depends()
    )
    delete_assistant_use_case: IDeleteAssistantUseCase = Depends()

    @command_router.post("/", dependencies=[], status_code=status.HTTP_201_CREATED)
    async def create(
        self,
        request: CreateAssistantRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> IDResponse:
        assistant_id = await self.create_assistant_use_case.execute(
            CreateAssistantCommand(
                user_id=descriptor.identity_id,
                name=request.name,
                description=request.description,
                prompt=request.prompt,
            )
        )
        return IDResponse(id=assistant_id)

    @command_router.put(
        "/{assistant_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update_info(
        self,
        assistant_id: UUID,
        request: UpdateAssistantInfoRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_assistant_info_use_case.execute(
            UpdateAssistantInfoCommand(
                user_id=descriptor.identity_id,
                assistant_id=assistant_id,
                name=request.name,
                description=request.description,
            )
        )

    @command_router.put(
        "/{assistant_id:uuid}/instructions",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def update_instructions(
        self,
        assistant_id: UUID,
        request: UpdateAssistantInstructionsRequest,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.update_assistant_instructions_use_case.execute(
            UpdateAssistantInstructionsCommand(
                user_id=descriptor.identity_id,
                assistant_id=assistant_id,
                prompt=request.prompt,
            )
        )

    @command_router.delete(
        "/{assistant_id:uuid}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete(
        self,
        assistant_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> None:
        await self.delete_assistant_use_case.execute(
            DeleteAssistantCommand(
                user_id=descriptor.identity_id,
                assistant_id=assistant_id,
            )
        )


query_router = APIRouter()


@cbv(query_router)
class AssistantQueryController:
    get_assistant_by_id_use_case: IGetAssistantByIdUseCase = Depends()
    list_assistants_use_case: IListAssistantsUseCase = Depends()

    @query_router.get("/")
    async def list_assistants(
        self,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> list[AssistantSummaryResponse]:
        read_models = await self.list_assistants_use_case.execute(
            ListAssistantsQuery(user_id=descriptor.identity_id)
        )
        return [AssistantSummaryResponse.from_read_model(m) for m in read_models]

    @query_router.get("/{assistant_id:uuid}")
    async def get_assistant(
        self,
        assistant_id: UUID,
        descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
    ) -> AssistantResponse:
        read_model = await self.get_assistant_by_id_use_case.execute(
            GetAssistantByIdQuery(
                user_id=descriptor.identity_id, assistant_id=assistant_id
            )
        )
        return AssistantResponse.from_read_model(read_model)
