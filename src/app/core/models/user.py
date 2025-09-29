from sqlmodel import Field

from app.core.models.base import SmartCityBqBaseModel


class UserBase(SmartCityBqBaseModel):
    login_name: str = Field(index=True)
    name: str = Field()
    identification: str = Field(index=True)


class DbUser(UserBase, table=True):
    __tablename__ = "users"
    password: str = Field()
