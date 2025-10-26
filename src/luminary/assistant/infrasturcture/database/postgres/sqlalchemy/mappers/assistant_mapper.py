from luminary.assistant.domain.entity.assisnant import (
    Assistant,
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
            assistant_id=base.assistant_id,
            user_id=base.user_id,
            info=AssistantInfo(name=base.name, description=base.description),
            instructions=Instructions(base.prompt),
        )

    @classmethod
    def to_persistence(cls, assistant: Assistant) -> AssistantBase:
        return AssistantBase(
            assistant_id=assistant.assistant_id,
            user_id=assistant.user_id,
            name=assistant.info.name,
            description=assistant.info.description,
            prompt=assistant.instructions.prompt,
        )
