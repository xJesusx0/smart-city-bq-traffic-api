from datetime import datetime
from typing import Any, Dict, Literal

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
    id: int | None = None
    street_a_id: int | None = None
    street_a_name: str | None = None
    street_b_id: int | None = None
    street_b_name: str | None = None
    distance_meters: float | None = None
    geojson: Dict[str, Any] | None = None


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


class IntersectionHeartbeat(BaseModel):
    device_name: str
    ip: str
    semaforo1_verde: int
    semaforo2_verde: int
    all_red_time: int
    estado_restante_s: int
    ciclo_restante_s: int
    next_semaforo1: int
    next_semaforo2: int
    next_fetched: bool
    estado: Literal[
        "S1_VERDE",
        "S1_AMARILLO",
        "S1_ROJO",
        "S2_VERDE",
        "S2_AMARILLO",
        "S2_ROJO",
        "S1_ROJO_AMARILLO",
        "S2_ROJO_AMARILLO",
        "ALL_RED",
    ]


class IntersectionState(IntersectionHeartbeat):
    intersection_id: int
    last_seen: int


class IntersectionWithStatus(Intersection):
    realtime_data: IntersectionState | None = None


class HeartbeatResponse(BaseModel):
    status: str
