from typing import Optional

from sqlmodel import Field

from app.core.models.base import SmartCityBqBaseModel


class LocationBase(SmartCityBqBaseModel):
    name: str = Field(index=True)
    description: Optional[str] = Field()
    latitude: Optional[float] = Field(nullable=False)
    longitude: Optional[float] = Field(nullable=False)


class DbLocation(LocationBase, table=True):
    __tablename__ = "locations"  # type: ignore


class LocationCreate(LocationBase):
    pass


from sqlmodel import SQLModel


class LocationUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
