from common.domain.value_objects.id import UserId

from luminary.assistant.application.dtos.read_models import (
    AssistantReadModel,
    AssistantSummaryReadModel,
)
from luminary.assistant.domain.entity.assistant import (
    Assistant,
    AssistantId,
    AssistantInfo,
    Instructions,
)
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)


class AssistantMapper:
    @classmethod
    def to_domain(cls, base: AssistantBase) -> Assistant:
        return Assistant(
            id=AssistantId(base.assistant_id),
            owner_id=UserId(base.owner_id),
            type=base.type,
            info=AssistantInfo(name=base.name, description=base.description),
            instructions=Instructions(prompt=base.prompt),
            is_deleted=base.is_deleted,
        )

    @classmethod
    def to_persistence(cls, assistant: Assistant) -> AssistantBase:
        return AssistantBase(
            assistant_id=assistant.id.value,
            owner_id=assistant.owner_id.value,
            type=assistant.type,
            name=assistant.info.name,
            description=assistant.info.description,
            prompt=assistant.instructions.prompt,
            is_deleted=assistant.is_deleted,
        )


class AssistantReadMapper:
    @classmethod
    def to_read(cls, base: AssistantBase) -> AssistantReadModel:
        return AssistantReadModel(
            id=base.assistant_id,
            name=base.name,
            description=base.description,
            type=base.type.value,
            prompt=base.prompt,
            created_at=base.created_at,
        )

    @classmethod
    def to_summary(cls, base: AssistantBase) -> AssistantSummaryReadModel:
        return AssistantSummaryReadModel(
            id=base.assistant_id,
            name=base.name,
            description=base.description,
            type=base.type.value,
        )
