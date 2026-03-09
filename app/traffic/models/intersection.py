from typing import Literal

from pydantic import BaseModel
from app.geo.models.geo_info_service_models import Intersection


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
