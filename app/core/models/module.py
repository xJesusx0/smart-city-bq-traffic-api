from typing import Optional
from sqlmodel import Field
from app.core.models.base import SmartCityBqBaseModel


class ModuleBase(SmartCityBqBaseModel):
    name: str = Field(index=True)
    description: Optional[str] = Field()
    path: str = Field()
    icon: str = Field()


class DbModule(ModuleBase, table=True):
    __tablename__ = "modules"
