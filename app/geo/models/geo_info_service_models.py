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
