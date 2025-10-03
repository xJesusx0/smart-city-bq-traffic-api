from typing import Optional
from sqlmodel import Field
from app.core.models.base import SmartCityBqBaseModel


class RoleBase(SmartCityBqBaseModel):
    name: str = Field(index=True)
    description: Optional[str] = Field()


class DbRole(RoleBase, table=True):
    __tablename__ = "roles"
