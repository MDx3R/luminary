from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import (
    Assistant,
    AssistantId,
    AssistantInfo,
    Instructions,
)
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)


class AssistantMapper:
    @classmethod
    def to_domain(cls, base: AssistantBase) -> Assistant:
        return Assistant(
            id=AssistantId(base.assistant_id),
            owner_id=UserId(base.user_id),
            info=AssistantInfo(name=base.name, description=base.description),
            instructions=Instructions(base.prompt),
            is_deleted=base.is_deleted,
        )

    @classmethod
    def to_persistence(cls, assistant: Assistant) -> AssistantBase:
        return AssistantBase(
            assistant_id=assistant.id.value,
            user_id=assistant.owner_id.value,
            name=assistant.info.name,
            description=assistant.info.description,
            prompt=assistant.instructions.prompt,
            is_deleted=assistant.is_deleted,
        )
