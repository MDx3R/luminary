from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from common.domain.value_objects.order_key import order_key_between

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.reorder_chats_use_case import (
    IReorderChatsUseCase,
    ReorderChatsCommand,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)


class ReorderChatsUseCase(IReorderChatsUseCase):
    def __init__(
        self,
        chat_repository: IChatRepository,
        folder_repository: IFolderRepository,
        folder_access_policy: IFolderAccessPolicy,
        chat_access_policy: IChatAccessPolicy,
    ) -> None:
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository
        self.folder_access_policy = folder_access_policy
        self.chat_access_policy = chat_access_policy

    async def execute(self, command: ReorderChatsCommand) -> None:
        owner_id = UserId(command.user_id)
        chat = await self.chat_repository.get_by_id(ChatId(command.chat_id))
        self.chat_access_policy.assert_is_allowed(owner_id, chat)
        if chat.folder_id is not None:
            folder = await self.folder_repository.get_by_id(chat.folder_id)
            self.folder_access_policy.assert_is_allowed(owner_id, folder)

        previous = await self._neighbour_key(chat, command.previous_chat_id)
        following = await self._neighbour_key(chat, command.next_chat_id)
        chat.change_order(order_key_between(previous, following))
        await self.chat_repository.save(chat)

    async def _neighbour_key(self, chat: Chat, neighbour_id: UUID | None) -> str | None:
        if neighbour_id is None:
            return None
        if neighbour_id == chat.id.value:
            raise InvariantViolationError("A chat cannot be its own order neighbour")
        neighbour = await self.chat_repository.get_by_id(ChatId(neighbour_id))
        self.chat_access_policy.assert_is_allowed(chat.owner_id, neighbour)
        if neighbour.folder_id != chat.folder_id:
            raise InvariantViolationError(
                "Order neighbours must be in the same location"
            )
        return neighbour.order_key
