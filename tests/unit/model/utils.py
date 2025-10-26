from decimal import Decimal
from uuid import UUID, uuid4

from luminary.model.domain.entity.model import Model


def make_model(
    model_id: UUID | None = None,
    name: str = "Test Model",
    description: str = "Test Description",
    input_price: Decimal = Decimal("0.0020"),
    output_price: Decimal = Decimal("0.0060"),
) -> Model:
    return Model.create(
        model_id=model_id or uuid4(),
        name=name,
        description=description,
        input_price=input_price,
        output_price=output_price,
    )
