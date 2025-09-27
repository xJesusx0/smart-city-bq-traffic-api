from sqlmodel import SQLModel, Field
from pydantic import BaseModel

from app.core.models.base import SmartCityBqBaseModel


class UserBase(SmartCityBqBaseModel):
    login_name: str | None = Field(index=True)
    name: str | None = Field()
    identification: str | None = Field(index=True)

class DbUser(UserBase, table=True):
    __tablename__ = "users"
    password: str | None = Field()