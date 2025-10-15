from sqlmodel import Session, select

from app.core.models.locations import DbLocation, LocationUpdate
from app.core.repositories.location_repository import LocationRepository


class LocationRepositoryImpl(LocationRepository):
    def __init__(self, session: Session):
        self.session = session

    def create_location(self, location: DbLocation) -> DbLocation:
        db_location = DbLocation.model_validate(location)
        self.session.add(db_location)
        self.session.commit()
        self.session.refresh(db_location)
        return db_location

    def get_location_by_id(self, location_id: int) -> DbLocation | None:
        return self.session.get(DbLocation, location_id)

    def get_all_locations(self) -> list[DbLocation]:
        return list(self.session.exec(select(DbLocation)).all())

    def get_all_locations_by_active(self, active: bool) -> list[DbLocation]:
        return list(
            self.session.exec(
                select(DbLocation).where(DbLocation.active == active)
            ).all()
        )

    def update_location(
        self, location_id: int, location: LocationUpdate
    ) -> DbLocation | None:
        db_location = self.get_location_by_id(location_id)
        if db_location:
            update_data = location.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_location, key, value)
            self.session.add(db_location)
            self.session.commit()
            self.session.refresh(db_location)
        return db_location

    def delete_location(self, location_id: int) -> DbLocation | None:
        db_location = self.get_location_by_id(location_id)
        if db_location:
            db_location.active = False
            self.session.add(db_location)
            self.session.commit()
            self.session.refresh(db_location)
        return db_location
