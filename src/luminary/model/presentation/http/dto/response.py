from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from luminary.model.application.dto.model_dto import ModelDTO


class ModelResponse(BaseModel):
    model_id: UUID
    name: str
    description: str
    input_price: Decimal
    output_price: Decimal

    @classmethod
    def from_dto(cls, dto: ModelDTO) -> Self:
        return cls(
            model_id=dto.model_id,
            name=dto.name,
            description=dto.description,
            input_price=dto.input_price,
            output_price=dto.output_price,
        )
