from typing import Optional

from sqlmodel import Field, SQLModel

from app.core.models.base import SmartCityBqBaseModel


class UserBase(SmartCityBqBaseModel):
    email: str = Field(index=True, unique=True)
    name: str = Field()
    identification: str = Field(index=True, unique=True)

    @classmethod
    def map_from_db(cls, db_user: "DbUser") -> "UserBase":
        return UserBase(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            identification=db_user.identification,
            creation_date=db_user.creation_date,
            active=db_user.active,
            update_date=db_user.update_date,
        )


class UserCreate(UserBase):
    roles: list[int]
    password: str


class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    roles: Optional[list[int]] = None


class DbUser(UserBase, table=True):
    __tablename__ = "users"
    password: str = Field()
