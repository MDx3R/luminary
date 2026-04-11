from pydantic import BaseModel


class RabbitMQConfig(BaseModel):
    queue_name: str
    rabbit_host: str
    rabbit_port: int
    rabbit_user: str
    rabbit_pass: str
    rabbit_vhost: str = "/"
    rabbit_ssl: bool = False

    @property
    def url(self) -> str:
        scheme = "amqps" if self.rabbit_ssl else "amqp"
        return (
            f"{scheme}://{self.rabbit_user}:{self.rabbit_pass}"
            f"@{self.rabbit_host}:{self.rabbit_port}/{self.rabbit_vhost}"
        )
