from typing import Annotated
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.auth import get_descriptor, require_authenticated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
    ICreateAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.delete_assistant_use_case import (
    DeleteAssistantCommand,
    IDeleteAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_use_case import (
    IUpdateAssistantUseCase,
    UpdateAssistantCommand,
)
from luminary.assistant.presentation.http.dto.request import (
    CreateAssistantRequest,
    UpdateAssistantRequest,
)


assistant_command_router = APIRouter()


@cbv(assistant_command_router)
class AssitantCommandController:
    create_assistant_use_case: ICreateAssistantUseCase = Depends()
    update_assistant_use_case: IUpdateAssistantUseCase = Depends()
    delete_assistant_use_case: IDeleteAssistantUseCase = Depends()

    @assistant_command_router.post("/", dependencies=[Depends(require_authenticated)])
    async def create(
        self,
        request: CreateAssistantRequest,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> IDResponse:
        try:
            assistant_id = await self.create_assistant_use_case.execute(
                CreateAssistantCommand(
                    descriptor, request.name, request.description, request.prompt
                )
            )
            return IDResponse(id=assistant_id)
        except AssistantDuplicateNameError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "AssistantDuplicateNameError",
                    "name": exc.name,
                    "message": str(exc),
                },
            ) from exc

    @assistant_command_router.patch(
        "/{assistant_id}", dependencies=[Depends(require_authenticated)]
    )
    async def update(
        self,
        assistant_id: UUID,
        request: UpdateAssistantRequest,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> None:
        try:
            await self.update_assistant_use_case.execute(
                UpdateAssistantCommand(
                    assistant_id=assistant_id,
                    user_id=descriptor,
                    name=request.name,
                    description=request.description,
                    prompt=request.prompt,
                )
            )
        except NotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "AssistantNotFoundError",
                    "assistant_id": str(exc.entity_id),
                    "message": str(exc),
                },
            ) from exc

    @assistant_command_router.delete(
        "/{assistant_id}", dependencies=[Depends(require_authenticated)]
    )
    async def delete(
        self,
        assistant_id: UUID,
        descriptor: Annotated[UUID, Depends(get_descriptor)],
    ) -> None:
        try:
            await self.delete_assistant_use_case.execute(
                DeleteAssistantCommand(assistant_id=assistant_id, user_id=descriptor)
            )
        except NotFoundError:
            return
