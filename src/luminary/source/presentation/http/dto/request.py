from pydantic import BaseModel


class CreateFileSourceRequest(BaseModel):
    title: str
