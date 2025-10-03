from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class SmartCityBqBaseModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
    active: bool = Field(default=True)
    creation_date: datetime = Field(default_factory=datetime.now)
    update_date: Optional[datetime] = Field(default=None)
