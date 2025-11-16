from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from tests.unit.chat.utils import make_chat_dto, make_chat_list_item_dto

from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    GetChatQuery,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    GetUserChatsQuery,
)
from luminary.chat.presentation.http.dto.response import (
    ChatListItemResponse,
    ChatResponse,
)
from luminary.chat.presentation.http.fastapi.controllers import ChatQueryController


@pytest.mark.asyncio
class TestChatQueryController:
    async def test_get_chat_returns_chat_response_on_success(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()
        folder_id = uuid4()

        chat_dto = make_chat_dto(
            chat_id=chat_id,
            user_id=user_id,
            model_id=model_id,
            folder_id=folder_id,
        )

        get_chat_use_case = AsyncMock()
        get_chat_use_case.execute.return_value = chat_dto

        get_user_chats_use_case = AsyncMock()

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        response = await controller.get_chat(
            chat_id=chat_id,
            descriptor=user_id,
        )

        assert isinstance(response, ChatResponse)
        assert response.chat_id == chat_id
        assert response.user_id == user_id
        assert response.model_id == model_id
        assert response.folder_id == folder_id

        get_chat_use_case.execute.assert_awaited_once()
        call_args = get_chat_use_case.execute.call_args[0][0]
        assert isinstance(call_args, GetChatQuery)
        assert call_args.user_id == user_id
        assert call_args.chat_id == chat_id

    async def test_get_chat_raises_not_found_error_when_chat_not_exists(
        self,
    ) -> None:
        user_id = uuid4()
        chat_id = uuid4()

        get_chat_use_case = AsyncMock()
        get_chat_use_case.execute.side_effect = NotFoundError(str(chat_id))

        get_user_chats_use_case = AsyncMock()

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        with pytest.raises(NotFoundError):
            await controller.get_chat(
                chat_id=chat_id,
                descriptor=user_id,
            )

    async def test_get_chat_calls_use_case_with_correct_query(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()

        chat_dto = make_chat_dto(chat_id=chat_id, user_id=user_id)

        get_chat_use_case = AsyncMock()
        get_chat_use_case.execute.return_value = chat_dto

        get_user_chats_use_case = AsyncMock()

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        await controller.get_chat(
            chat_id=chat_id,
            descriptor=user_id,
        )

        assert get_chat_use_case.execute.call_count == 1
        call_args = get_chat_use_case.execute.call_args[0][0]
        assert call_args.user_id == user_id
        assert call_args.chat_id == chat_id

    async def test_get_user_chats_returns_list_of_chats_without_folder_filter(
        self,
    ) -> None:
        user_id = uuid4()

        chat_dtos = [
            make_chat_list_item_dto(name="Chat 1"),
            make_chat_list_item_dto(name="Chat 2"),
            make_chat_list_item_dto(name="Chat 3"),
        ]
        expected_count = len(chat_dtos)

        get_chat_use_case = AsyncMock()

        get_user_chats_use_case = AsyncMock()
        get_user_chats_use_case.execute.return_value = chat_dtos

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        response = await controller.get_user_chats(
            descriptor=user_id,
            folder_id=None,
        )

        assert isinstance(response, list)
        assert len(response) == expected_count
        assert all(isinstance(item, ChatListItemResponse) for item in response)
        assert response[0].name == "Chat 1"
        assert response[1].name == "Chat 2"
        assert response[2].name == "Chat 3"

        get_user_chats_use_case.execute.assert_awaited_once()
        call_args = get_user_chats_use_case.execute.call_args[0][0]
        assert isinstance(call_args, GetUserChatsQuery)
        assert call_args.user_id == user_id
        assert call_args.folder_id is None

    async def test_get_user_chats_returns_list_of_chats_with_folder_filter(
        self,
    ) -> None:
        user_id = uuid4()
        folder_id = uuid4()

        chat_dtos = [
            make_chat_list_item_dto(name="Folder Chat 1"),
            make_chat_list_item_dto(name="Folder Chat 2"),
        ]
        expected_count = len(chat_dtos)

        get_chat_use_case = AsyncMock()

        get_user_chats_use_case = AsyncMock()
        get_user_chats_use_case.execute.return_value = chat_dtos

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        response = await controller.get_user_chats(
            descriptor=user_id,
            folder_id=folder_id,
        )

        assert isinstance(response, list)
        assert len(response) == expected_count
        assert response[0].name == "Folder Chat 1"
        assert response[1].name == "Folder Chat 2"

        get_user_chats_use_case.execute.assert_awaited_once()
        call_args = get_user_chats_use_case.execute.call_args[0][0]
        assert call_args.user_id == user_id
        assert call_args.folder_id == folder_id

    async def test_get_user_chats_returns_empty_list_when_no_chats(self) -> None:
        user_id = uuid4()

        get_chat_use_case = AsyncMock()

        get_user_chats_use_case = AsyncMock()
        get_user_chats_use_case.execute.return_value = []

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        response = await controller.get_user_chats(
            descriptor=user_id,
            folder_id=None,
        )

        assert isinstance(response, list)
        assert len(response) == 0

    async def test_get_user_chats_calls_use_case_with_correct_query(self) -> None:
        user_id = uuid4()
        folder_id = uuid4()

        get_chat_use_case = AsyncMock()

        get_user_chats_use_case = AsyncMock()
        get_user_chats_use_case.execute.return_value = []

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        await controller.get_user_chats(
            descriptor=user_id,
            folder_id=folder_id,
        )

        assert get_user_chats_use_case.execute.call_count == 1
        call_args = get_user_chats_use_case.execute.call_args[0][0]
        assert call_args.user_id == user_id
        assert call_args.folder_id == folder_id

    async def test_get_chat_response_contains_all_fields(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()
        folder_id = uuid4()

        chat_name = "Test Chat"
        system_prompt = "Test system prompt"
        max_context = 15

        chat_dto = make_chat_dto(
            chat_id=chat_id,
            user_id=user_id,
            model_id=model_id,
            folder_id=folder_id,
            name=chat_name,
            system_prompt=system_prompt,
            max_context_messages=max_context,
        )

        get_chat_use_case = AsyncMock()
        get_chat_use_case.execute.return_value = chat_dto

        get_user_chats_use_case = AsyncMock()

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        response = await controller.get_chat(
            chat_id=chat_id,
            descriptor=user_id,
        )

        assert response.chat_id == chat_id
        assert response.user_id == user_id
        assert response.model_id == model_id
        assert response.folder_id == folder_id
        assert response.name == chat_name
        assert response.system_prompt == system_prompt
        assert response.max_context_messages == max_context
        assert response.created_at == chat_dto.created_at
        assert response.updated_at == chat_dto.updated_at

    async def test_get_user_chats_response_contains_all_fields(self) -> None:
        user_id = uuid4()
        chat_id = uuid4()
        chat_name = "Test Chat Item"

        chat_dto = make_chat_list_item_dto(
            chat_id=chat_id,
            name=chat_name,
        )

        get_chat_use_case = AsyncMock()

        get_user_chats_use_case = AsyncMock()
        get_user_chats_use_case.execute.return_value = [chat_dto]

        controller = ChatQueryController(  # type: ignore[call-arg]
            get_chat_use_case=get_chat_use_case,
            get_user_chats_use_case=get_user_chats_use_case,
        )

        response = await controller.get_user_chats(
            descriptor=user_id,
            folder_id=None,
        )

        assert len(response) == 1
        assert response[0].chat_id == chat_id
        assert response[0].name == chat_name
        assert response[0].created_at == chat_dto.created_at
        assert response[0].updated_at == chat_dto.updated_at
