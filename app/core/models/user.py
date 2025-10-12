from app.core.models.user_role import DbUserRole
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

from app.core.models.base import SmartCityBqBaseModel


class UserBase(SmartCityBqBaseModel):
    login_name: str = Field(index=True, unique=True)
    name: str = Field()
    identification: str = Field(index=True, unique=True)

    @classmethod
    def map_from_db(cls, db_user: "DbUser") -> "UserBase":
        return UserBase(
            id=db_user.id,
            login_name=db_user.login_name,
            name=db_user.name,
            identification=db_user.identification,
            creation_date=db_user.creation_date,
            active=db_user.active,
            update_date=db_user.update_date,
        )


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    login_name: Optional[str] = None
    name: Optional[str] = None


class DbUser(UserBase, table=True):
    __tablename__ = "users"
    password: str = Field()
