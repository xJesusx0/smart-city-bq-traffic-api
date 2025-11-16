import httpx

from app.core.exceptions import get_forbidden_exception
from app.geo.models.geo_info_service_models import NeighborhoodInfo


class GeoInfoService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def get_neighborhood_by_point(
        self, latitude: float, longitude: float
    ) -> NeighborhoodInfo | None:
        url = f"{self.base_url}/api/v1/neighborhoods/point?latitude={latitude}&longitude={longitude}"
        response = await self.send_request(url)
        if response.status_code == 200:
            data = response.json()
            return NeighborhoodInfo(**data)
        elif response.status_code == 403:
            raise get_forbidden_exception(f"Acceso denegado a la API de información geográfica")
        else:
            return None

    async def send_request(self, url: str) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"x-api-key": self.api_key})
            return response
