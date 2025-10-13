from pydantic import BaseModel


class GoogleTokenRequest(BaseModel):
    token: str


class GoogleUserInfo(BaseModel):
    email: str | None
    name: str | None
    picture: str | None
    sub: str | None
