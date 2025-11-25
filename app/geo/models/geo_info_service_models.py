from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class NeighborhoodInfo(BaseModel):
    neighborhood_id: int
    neighborhood_name: str
    city_id: int
    city_name: str
    city_dane_code: str
    department_id: int
    department_name: str
    department_dane_code: str
    country_id: int
    country_name: str
    locality_name: str
    urban_area_name: str


class Intersection(BaseModel):
    intersection_id: int
    street_a_id: int
    street_a_name: str
    street_b_id: int
    street_b_name: str
    distance_meters: float
    geojson: Dict[str, Any]


class CreateIntersectionDTO(BaseModel):
    street_a_id: int
    street_b_id: int


class IntersectionQueryParams(BaseModel):
    latitude: float
    longitude: float
    radius: int
    limit: int


class TrafficLight(BaseModel):
    id: int | None = None
    name: str | None = None
    intersection_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    key_hash: str | None = None
    active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    key: str | None = None


class CreateTrafficLightDTO(BaseModel):
    name: str
    intersection_id: int
    latitude: float
    longitude: float
