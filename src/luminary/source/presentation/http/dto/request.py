from pydantic import BaseModel


class CreateFileSourceRequest(BaseModel):
    title: str


class CreatePageSourceRequest(BaseModel):
    title: str


class CreateLinkSourceRequest(BaseModel):
    title: str
    url: str


class UpdateSourceRequest(BaseModel):
    title: str
