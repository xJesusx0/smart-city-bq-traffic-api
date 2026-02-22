from pydantic import BaseModel


class OauthTokenRequest(BaseModel):
    token: str


class GoogleUserInfo(BaseModel):
    email: str | None
    name: str | None
    picture: str | None
    sub: str | None


class MicrosoftUserInfo(BaseModel):
    email: str | None
    name: str | None
