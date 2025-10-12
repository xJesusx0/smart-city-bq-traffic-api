from pydantic import BaseModel


class DatasetResponse(BaseModel):
    label: str
    data: list[float]
    border_color: str
    background_color: str
    tension: float


class TimeLineResponse(BaseModel):
    labels: list[str]
    data: list[DatasetResponse]
