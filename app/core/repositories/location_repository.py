from abc import ABC, abstractmethod

from app.core.models.locations import DbLocation, LocationCreate, LocationUpdate


class LocationRepository(ABC):
    @abstractmethod
    def create_location(self, location: LocationCreate) -> DbLocation:
        pass

    @abstractmethod
    def get_location_by_id(self, location_id: int) -> DbLocation | None:
        pass

    @abstractmethod
    def get_all_locations(self) -> list[DbLocation]:
        pass

    @abstractmethod
    def get_all_locations_by_active(self, active: bool) -> list[DbLocation]:
        pass

    @abstractmethod
    def update_location(
        self, location_id: int, location: LocationUpdate
    ) -> DbLocation | None:
        pass

    @abstractmethod
    def delete_location(self, location_id: int) -> DbLocation | None:
        pass
