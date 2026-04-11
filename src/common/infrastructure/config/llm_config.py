from typing import Self

from pydantic import BaseModel, model_validator


class LLMConfig(BaseModel):
    model: str
    provider_model: str = ""
    base_url: str
    api_key: str | None = None
    embed_model: str
    provider_embed_model: str = ""

    @model_validator(mode="after")
    def default_provider_model(self) -> Self:
        if not self.provider_model:
            self.provider_model = self.model
        if not self.provider_embed_model:
            self.provider_embed_model = self.embed_model
        return self
