from typing import Optional
from sqlmodel import Field, SQLModel
from app.core.models.base import SmartCityBqBaseModel


class RoleBase(SmartCityBqBaseModel):
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)


class DbRole(RoleBase, table=True):
    __tablename__ = "roles"


class RoleCreate(RoleBase):
    pass


class RoleUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
