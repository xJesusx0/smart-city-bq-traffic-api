from fastapi import APIRouter

from app.core.dependencies import GeoInfoServiceDep
from app.core.exceptions import get_entity_not_found_exception
from app.geo.models.geo_info_service_models import (
    Intersection,
    NeighborhoodInfo,
    TrafficLight,
)

geo_router = APIRouter(prefix="/api/geo", tags=["geo"])


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


@geo_router.get("/intersections")
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