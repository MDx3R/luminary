from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    message: str
