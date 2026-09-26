from abc import ABC, abstractmethod
from decimal import Decimal

from luminary.model.domain.entity.model import Model


class IModelFactory(ABC):
    @abstractmethod
    def create(
        self,
        name: str,
        description: str,
        input_price: Decimal,
        output_price: Decimal,
    ) -> Model: ...
