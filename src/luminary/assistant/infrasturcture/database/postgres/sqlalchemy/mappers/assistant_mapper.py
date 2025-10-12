from luminary.assistant.domain.entity.assisnant import Assistant, Instructions
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)


class AssistantMapper:
    @classmethod
    def to_domain(cls, base: AssistantBase) -> Assistant:
        inst = None
        if base.prompt:
            inst = Instructions(base.prompt)
        return Assistant(
            assistant_id=base.assistant_id,
            user_id=base.user_id,
            name=base.name,
            description=base.description,
            instructions=inst,
        )

    @classmethod
    def to_persistence(cls, assistant: Assistant) -> AssistantBase:
        inst = assistant.instructions
        prompt = inst.prompt if inst else None

        return AssistantBase(
            assistant_id=assistant.assistant_id,
            user_id=assistant.user_id,
            name=assistant.name,
            description=assistant.description,
            prompt=prompt,
        )
