from uuid import UUID

from common.application.exceptions import ApplicationError


class AssistantDuplicateNameError(ApplicationError):
    def __init__(self, user_id: UUID, name: str) -> None:
        super().__init__(
            f"Assistant with name {name} exists for user with id {user_id}"
        )
        self.user_id = user_id
        self.name = name
