from decimal import Decimal

from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.model.domain.entity.model import Model, ModelId
from luminary.model.domain.interfaces.model_factory import IModelFactory


class ModelFactory(IModelFactory):
    def __init__(self, uuid_generator: IUUIDGenerator) -> None:
        self.uuid_generator = uuid_generator

    def create(
        self,
        name: str,
        description: str,
        input_price: Decimal,
        output_price: Decimal,
    ) -> Model:
        return Model.create(
            id=ModelId(self.uuid_generator.create()),
            name=name,
            description=description,
            input_price=input_price,
            output_price=output_price,
        )
