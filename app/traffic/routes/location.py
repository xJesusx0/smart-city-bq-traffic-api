import logging
import traceback

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import LocationServiceDep
from app.core.exceptions import (
    get_bad_request_exception,
    get_conflict_exception,
    get_entity_not_found_exception,
    get_internal_server_error_exception,
)
from app.core.models.locations import LocationBase, LocationCreate, LocationUpdate

location_router = APIRouter(prefix="/api/traffic/locations", tags=["locations"])


@location_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=LocationBase
)
def create_location(location: LocationCreate, location_service: LocationServiceDep):
    if not location.name:
        raise get_bad_request_exception("El nombre de la ubicación es obligatorio.")
    try:
        return location_service.create_location(location)
    except IntegrityError:
        print(traceback.format_exc())
        raise get_conflict_exception(
            f"Ya existe una ubicación con el nombre '{location.name}'."
        )
    except Exception as e:
        logging.error(f"Error al guardar una ubicación: {e}")
        raise get_internal_server_error_exception(
            "Ocurrió un error inesperado, contacte con un administrador"
        )


@location_router.get("", response_model=list[LocationBase])
def get_all_locations(
    location_service: LocationServiceDep, active: bool | None = None
):
    return location_service.get_all_locations(active=active)


@location_router.get("/{location_id}", response_model=LocationBase)
def get_location_by_id(location_id: int, location_service: LocationServiceDep):
    location = location_service.get_location_by_id(location_id)
    if location is None:
        raise get_entity_not_found_exception(
            f"Ubicación con id {location_id} no encontrada"
        )
    return location


@location_router.put("/{location_id}", response_model=LocationBase)
def update_location(
    location_id: int, location: LocationUpdate, location_service: LocationServiceDep
):
    try:
        updated_location = location_service.update_location(location_id, location)
        if updated_location is None:
            raise get_entity_not_found_exception(
                f"Ubicación con id {location_id} no encontrada"
            )
        return updated_location
    except IntegrityError:
        raise get_conflict_exception(
            f"Ya existe una ubicación con el nombre '{location.name}'"
        )
    except Exception as e:
        logging.error(f"Error al actualizar una ubicación: {e}")
        raise get_internal_server_error_exception(
            "Ocurrió un error inesperado, contacte con un administrador"
        )


@location_router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, location_service: LocationServiceDep):
    deleted_location = location_service.delete_location(location_id)
    if deleted_location is None:
        raise get_entity_not_found_exception(
            f"Ubicación con id {location_id} no encontrada"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
