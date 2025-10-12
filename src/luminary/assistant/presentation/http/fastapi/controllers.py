from typing import Annotated
from uuid import UUID

from common.presentation.http.dto.response import IDResponse
from common.presentation.http.fastapi.auth import get_descriptor, require_authenticated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
    ICreateAssistantUseCase,
)
from luminary.assistant.presentation.http.dto.request import CreateAssistantRequest


assistant_command_router = APIRouter()


@cbv(assistant_command_router)
class AssitantCommandController:
    create_assistant_use_case: ICreateAssistantUseCase = Depends()

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
