from dataclasses import dataclass
from decimal import Decimal
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError


@dataclass
class Model:
    model_id: UUID
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
        model_id: UUID,
        name: str,
        description: str,
        input_price: Decimal,
        output_price: Decimal,
    ) -> Self:
        return cls(model_id, name, description, input_price, output_price)
