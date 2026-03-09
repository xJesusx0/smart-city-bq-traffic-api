import json
import time

from fastapi import APIRouter, Depends

from app.core.database.redis import get_redis_client
from app.core.dependencies import GeoInfoServiceDep, validate_token
from app.core.exceptions import get_entity_not_found_exception
from app.geo.models.geo_info_service_models import (
    CreateIntersectionDTO,
    CreateTrafficLightDTO,
    HeartbeatResponse,
    Intersection,
    IntersectionHeartbeat,
    IntersectionState,
    IntersectionWithStatus,
    NeighborhoodInfo,
    TrafficLight,
)

# Router para rutas PÚBLICAS (No requieren JWT)
public_geo_router = APIRouter(prefix="/api/geo", tags=["geo-public"])

# Router para rutas PROTEGIDAS (Requieren JWT)
geo_router = APIRouter(
    prefix="/api/geo", tags=["geo"], dependencies=[Depends(validate_token)]
)


@public_geo_router.post(
    "/intersections/{intersection_id}/heartbeat", response_model=HeartbeatResponse
)
async def heartbeat(intersection_id: int, data: IntersectionHeartbeat):
    key = f"intersection:{intersection_id}:state"

    # Calculate last_seen
    last_seen = int(time.time())

    # Create the state object to be stored in Redis
    state = data.model_dump()
    state["intersection_id"] = intersection_id
    state["last_seen"] = last_seen

    # Get redis client and save data with 30s TTL
    redis_client = get_redis_client()
    redis_client.set(key, json.dumps(state), ex=30)

    return HeartbeatResponse(status="ok")


@geo_router.get("/neighborhoods/point")
async def get_neighborhood_by_point(
    latitude: float, longitude: float, geo_info_service: GeoInfoServiceDep
) -> NeighborhoodInfo:
    neighborhood = await geo_info_service.get_neighborhood_by_point(latitude, longitude)
    if neighborhood is None:
        raise get_entity_not_found_exception(
            f"No se encontró una vecindad para la latitud {latitude} y longitud {longitude}"
        )
    return neighborhood


@geo_router.get("/intersections/coordinates")
async def get_intersections_by_point(
    latitude: float, longitude: float, radius: int, geo_info_service: GeoInfoServiceDep
) -> list[Intersection]:
    intersections = await geo_info_service.get_intersection_by_point(
        latitude, longitude, radius
    )
    if intersections is None:
        raise get_entity_not_found_exception(
            f"No se encontraron intersecciones para la latitud {latitude} y longitud {longitude}"
        )
    return intersections


@geo_router.get("/intersections", response_model=list[IntersectionWithStatus])
async def get_all_intersections(geo_service: GeoInfoServiceDep):
    # 1. Fetch registered intersections from GeoInfoService
    registered_intersections = await geo_service.get_intersections()
    # 2. Fetch all real-time states from Redis
    redis_client = get_redis_client()
    keys = redis_client.keys("intersection:*:state")

    realtime_states = {}
    for key in keys:
        data = redis_client.get(key)
        if data:
            state = IntersectionState(**json.loads(data))
            realtime_states[state.intersection_id] = state

    # 3. Merge data
    results = []
    for intersection in registered_intersections:
        # Create IntersectionWithStatus from Intersection data
        intersection_with_status = IntersectionWithStatus(**intersection.model_dump())

        # Link real-time data if available
        if intersection.id in realtime_states:
            intersection_with_status.realtime_data = realtime_states[intersection.id]

        results.append(intersection_with_status)

    return results


@geo_router.post("/intersections")
async def create_intersection(
    intersection_dto: CreateIntersectionDTO,
    geo_info_service: GeoInfoServiceDep = GeoInfoServiceDep,
) -> Intersection:
    intersection = await geo_info_service.create_intersection(intersection_dto)
    if intersection is None:
        raise get_entity_not_found_exception("No se pudo crear la intersección")
    return intersection


@geo_router.post("/traffic-lights")
async def create_traffic_light(
    traffic_light_dto: CreateTrafficLightDTO,
    geo_info_service: GeoInfoServiceDep = GeoInfoServiceDep,
) -> TrafficLight:
    traffic_light = await geo_info_service.create_traffic_light(traffic_light_dto)
    if traffic_light is None:
        raise get_entity_not_found_exception("No se pudo crear el semáforo")
    return traffic_light


@geo_router.get("/traffic-lights")
async def get_traffic_lights(
    name: str | None = None,
    intersection_id: int | None = None,
    longitude: float | None = None,
    latitude: float | None = None,
    geo_info_service: GeoInfoServiceDep = GeoInfoServiceDep,
) -> list[TrafficLight | None]:
    traffic_lights = await geo_info_service.get_traffic_lights(
        name, intersection_id, longitude, latitude
    )
    if traffic_lights is None:
        raise get_entity_not_found_exception(
            f"No se encontraron semáforos para la latitud {latitude} y longitud {longitude}"
        )
    return traffic_lights


@geo_router.get("/traffic-lights/{traffic_light_id}")
async def get_traffic_light_by_id(
    traffic_light_id: int, geo_info_service: GeoInfoServiceDep = GeoInfoServiceDep
) -> TrafficLight:
    traffic_light = await geo_info_service.get_traffic_light_by_id(traffic_light_id)
    if traffic_light is None:
        raise get_entity_not_found_exception(
            f"No se encontró un semáforo con el id {traffic_light_id}"
        )
    return traffic_light
