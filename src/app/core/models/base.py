from typing import Optional

from sqlmodel import SQLModel, Field


class SmartCityBqBaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    active: bool | None = Field(default=True)
    creation_date: str | None = Field()
    update_date: str | None = Field()
