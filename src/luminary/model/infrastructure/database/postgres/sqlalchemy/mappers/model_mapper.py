from luminary.model.domain.entity.model import Model
from luminary.model.infrastructure.database.postgres.sqlalchemy.models.model_base import (
    ModelBase,
)


class ModelMapper:
    @classmethod
    def to_domain(cls, base: ModelBase) -> Model:
        return Model(
            model_id=base.model_id,
            name=base.name,
            description=base.description,
            input_price=base.input_price,
            output_price=base.output_price,
        )

    @classmethod
    def to_persistence(cls, model: Model) -> ModelBase:
        return ModelBase(
            model_id=model.model_id,
            name=model.name,
            description=model.description,
            input_price=model.input_price,
            output_price=model.output_price,
        )
