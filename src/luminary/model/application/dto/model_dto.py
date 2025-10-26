from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from luminary.model.domain.entity.model import Model


@dataclass(frozen=True)
class ModelDTO:
    model_id: UUID
    name: str
    description: str
    input_price: Decimal
    output_price: Decimal

    @classmethod
    def from_entity(cls, model: Model) -> "ModelDTO":
        return cls(
            model_id=model.model_id,
            name=model.name,
            description=model.description,
            input_price=model.input_price,
            output_price=model.output_price,
        )
