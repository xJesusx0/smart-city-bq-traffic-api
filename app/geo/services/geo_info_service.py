import httpx

from app.geo.models.geo_info_service_models import NeighborhoodInfo


class GeoInfoService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_neighborhood_by_point(
        self, latitude: float, longitude: float
    ) -> NeighborhoodInfo | None:
        url = f"{self.base_url}/api/v1/neighborhoods/point?latitude={latitude}&longitude={longitude}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return NeighborhoodInfo(**data)
            else:
                return None
