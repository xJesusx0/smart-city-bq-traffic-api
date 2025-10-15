from app.core.models.locations import DbLocation, LocationCreate, LocationUpdate
from app.core.repositories.location_repository import LocationRepository


class LocationService:
    def __init__(self, location_repository: LocationRepository):
        self.location_repository = location_repository

    def create_location(self, location: LocationCreate) -> DbLocation:
        return self.location_repository.create_location(location)

    def get_location_by_id(self, location_id: int) -> DbLocation | None:
        return self.location_repository.get_location_by_id(location_id)

    def get_all_locations(self, active: bool | None = None) -> list[DbLocation]:
        if active is None:
            return self.location_repository.get_all_locations()
        else:
            return self.location_repository.get_all_locations_by_active(active=active)

    def update_location(
        self, location_id: int, location: LocationUpdate
    ) -> DbLocation | None:
        return self.location_repository.update_location(location_id, location)

    def delete_location(self, location_id: int) -> DbLocation | None:
        return self.location_repository.delete_location(location_id)
