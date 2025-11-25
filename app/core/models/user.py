from typing import Optional

from sqlmodel import Field, SQLModel

from app.core.models.base import SmartCityBqBaseModel


class UserBase(SmartCityBqBaseModel):
    email: str = Field(index=True, unique=True)
    name: str = Field()
    identification: str = Field(index=True, unique=True)
    must_change_password: bool | None = Field(default=False)
    update_password_uuid: str | None = Field(default=None, unique=True)

    @classmethod
    def map_from_db(cls, db_user: "DbUser") -> "UserBase":
        return UserBase(**db_user.model_dump())


class UserCreate(UserBase):
    roles: list[int]


class UserCreateWithPassword(UserCreate):
    password: str


class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    active: Optional[bool] = None
    roles: Optional[list[int]] = None


class DbUser(UserBase, table=True):
    __tablename__ = "users"
    password: str = Field()
