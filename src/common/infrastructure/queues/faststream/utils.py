from common.infrastructure.config.rabbit_config import RabbitMQConfig
from faststream.rabbit import RabbitBroker


def create_rabbit(cfg: RabbitMQConfig) -> RabbitBroker:
    return RabbitBroker(cfg.url)
