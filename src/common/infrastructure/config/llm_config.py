from pydantic import BaseModel


class LLMConfig(BaseModel):
    model: str
    base_url: str
    api_key: str = ""
    embed_model: str
    max_tokes: int = 65536
