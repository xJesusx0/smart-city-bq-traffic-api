from fastapi import APIRouter, status, Response, HTTPException
from sqlalchemy.exc import IntegrityError
import logging

from app.core.dependencies import RoleServiceDep
from app.core.exceptions import (
    get_entity_not_found_exception,
    get_internal_server_error_exception,
    get_conflict_exception,
    get_bad_request_exception,
)
from app.core.models.role import RoleCreate, RoleUpdate, DbRole

role_router = APIRouter(prefix="/api/iam/roles", tags=["roles"])


@role_router.get("", response_model=list[DbRole])
def get_all_roles(role_service: RoleServiceDep):
    return role_service.get_all_roles()


@role_router.get("/{role_id}", response_model=DbRole)
def get_role_by_id(role_id: int, role_service: RoleServiceDep):
    role = role_service.get_role_by_id(role_id)
    if role is None:
        raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")

    return role


@role_router.post("", status_code=status.HTTP_201_CREATED, response_model=DbRole)
def create_role(role: RoleCreate, role_service: RoleServiceDep):
    if not role.name:
        raise get_bad_request_exception("El nombre del rol es obligatorio.")
    try:
        return role_service.create_role(role)
    except IntegrityError:
        raise get_conflict_exception(f"Ya existe un rol con el nombre '{role.name}'.")
    except Exception as e:
        logging.error(f"Error al guardar un rol: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )


@role_router.put("/{role_id}", response_model=DbRole)
def update_role(role_id: int, role: RoleUpdate, role_service: RoleServiceDep):
    if not role.name:
        raise get_bad_request_exception("El nombre del rol es obligatorio.")
    try:
        updated_role = role_service.update_role(role_id, role)
        if updated_role is None:
            raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")
        return updated_role
    except HTTPException as e:
        raise e
    except IntegrityError:
        raise get_conflict_exception(f"Ya existe un rol con el nombre '{role.name}' ")
    except Exception as e:
        logging.error(f"Error al guardar un rol: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )


@role_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, role_service: RoleServiceDep):
    role = role_service.delete_role(role_id)
    if role is None:
        raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
