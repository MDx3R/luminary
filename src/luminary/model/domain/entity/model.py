from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import EntityId


@dataclass(frozen=True)
class ModelId(EntityId): ...


@dataclass
class Model:
    id: ModelId
    name: str
    description: str
    input_price: Decimal
    output_price: Decimal

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Model name cannot be empty")
        if not self.description.strip():
            raise InvariantViolationError("Model description cannot be empty")
        if self.input_price < 0:
            raise InvariantViolationError("Input price cannot be negative")
        if self.output_price < 0:
            raise InvariantViolationError("Output price cannot be negative")

    @classmethod
    def create(
        cls,
        id: ModelId,
        name: str,
        description: str,
        input_price: Decimal,
        output_price: Decimal,
    ) -> Self:
        return cls(
            id=id,
            name=name,
            description=description,
            input_price=input_price,
            output_price=output_price,
        )
