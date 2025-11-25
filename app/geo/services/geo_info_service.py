import httpx

from app.core.exceptions import (
    get_bad_request_exception,
    get_conflict_exception,
    get_forbidden_exception,
    get_internal_server_error_exception,
    get_entity_not_found_exception,
)
from app.geo.models.geo_info_service_models import (
    CreateIntersectionDTO,
    CreateTrafficLightDTO,
    Intersection,
    NeighborhoodInfo,
    TrafficLight,
)


class GeoInfoService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Maneja las respuestas de error de la API externa.
        
        Formato esperado de error:
        {
            "message": "Descripción del error",
            "error": "TipoDeError",
            "statusCode": 400
        }
        """
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Error desconocido")
        except Exception:
            error_message = f"Error en la API externa: {response.status_code}"

        if response.status_code == 400:
            raise get_bad_request_exception(error_message)
        elif response.status_code == 403:
            raise get_forbidden_exception(error_message)
        elif response.status_code == 404:
            raise get_entity_not_found_exception(error_message)
        elif response.status_code == 409:
            raise get_conflict_exception(error_message)
        elif response.status_code >= 500:
            raise get_internal_server_error_exception(error_message)
        else:
            raise get_internal_server_error_exception(
                f"Error inesperado de la API externa: {error_message}"
            )

    async def get_neighborhood_by_point(
        self, latitude: float, longitude: float
    ) -> NeighborhoodInfo | None:
        url = f"{self.base_url}/api/v1/neighborhoods/point?latitude={latitude}&longitude={longitude}"
        response = await self.send_request(url)
        if response.status_code == 200:
            data: NeighborhoodInfo = response.json()
            return data
        else:
            self._handle_error_response(response)

    async def get_intersection_by_point(
        self, latitude: float, longitude: float, radius: int
    ) -> list[Intersection] | None:
        url = f"{self.base_url}/api/v1/intersections?latitude={latitude}&longitude={longitude}&radius={radius}&limit=10"
        response = await self.send_request(url)
        if response.status_code == 200:
            data: list = response.json()
            return [Intersection(**item) for item in data]
        else:
            self._handle_error_response(response)

    async def get_traffic_lights(
        self,
        name: str | None = None,
        intersection_id: int | None = None,
        longitude: float | None = None,
        latitude: float | None = None,
    ) -> list[TrafficLight] | None:
        url = f"{self.base_url}/api/v1/traffic-lights"
        params = {
            "name": name,
            "intersection_id": intersection_id,
            "longitude": longitude,
            "latitude": latitude,
        }
        # Filtrar parametros nulos para no enviarlos en la query string
        params = {k: v for k, v in params.items() if v is not None}

        response = await self.send_request(url, params=params)
        if response.status_code == 200:
            data: list = response.json()
            return [TrafficLight(**item) for item in data]
        else:
            self._handle_error_response(response)

    async def get_traffic_light_by_id(
        self, traffic_light_id: int
    ) -> TrafficLight | None:
        url = f"{self.base_url}/api/v1/traffic-lights/{traffic_light_id}"
        response = await self.send_request(url)
        if response.status_code == 200:
            data: dict = response.json()
            return TrafficLight(**data)
        else:
            self._handle_error_response(response)

    async def create_intersection(
        self, intersection_dto: CreateIntersectionDTO
    ) -> Intersection:
        url = f"{self.base_url}/api/v1/intersections"
        response = await self.send_post_request(url, body=intersection_dto.dict())
        if response.status_code == 200 or response.status_code == 201:
            data: dict = response.json()
            return Intersection(**data)
        else:
            self._handle_error_response(response)

    async def create_traffic_light(
        self, traffic_light_dto: CreateTrafficLightDTO
    ) -> TrafficLight:
        url = f"{self.base_url}/api/v1/traffic-lights"
        response = await self.send_post_request(url, body=traffic_light_dto.dict())
        if response.status_code == 200 or response.status_code == 201:
            data: dict = response.json()
            return TrafficLight(**data)
        else:
            self._handle_error_response(response)

    async def send_request(
        self, url: str, params: dict | None = None
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers={"x-api-key": self.api_key}
            )
            return response

    async def send_post_request(
        self, url: str, body: dict | None = None
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=body, headers={"x-api-key": self.api_key}
            )
            return response
