from fastapi import APIRouter

from app.core.dependencies import GeoInfoServiceDep
from app.geo.models.geo_info_service_models import NeighborhoodInfo
from app.core.exceptions import get_entity_not_found_exception

geo_router = APIRouter(prefix="/api/geo", tags=["geo"])

@geo_router.get("/neighborhoods/point")
async def get_neighborhood_by_point(latitude: float, longitude: float, geo_info_service: GeoInfoServiceDep) -> NeighborhoodInfo:
    neighborhood = await geo_info_service.get_neighborhood_by_point(latitude, longitude)
    if neighborhood is None:
        raise get_entity_not_found_exception(f"No se encontró una vecindad para la latitud {latitude} y longitud {longitude}")
    return neighborhood