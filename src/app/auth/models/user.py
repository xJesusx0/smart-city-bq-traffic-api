from sqlmodel import SQLModel, Field

from src.app.core.models.base import SmartCityBqBaseModel


class UserBase(SmartCityBqBaseModel):
    login_name: str | None = Field(index=True)
    name: str | None = Field()
    identification: str | None = Field(index=True)

class DbUser(UserBase, table=True):
    password: str | None = Field()