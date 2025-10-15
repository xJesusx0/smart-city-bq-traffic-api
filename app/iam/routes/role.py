import logging

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import (
    CreateRoleUseCaseDep,
    RoleServiceDep,
    UpdateRoleUseCaseDep,
)
from app.core.exceptions import (
    get_bad_request_exception,
    get_conflict_exception,
    get_entity_not_found_exception,
    get_internal_server_error_exception,
)
from app.core.models.role import RoleBase, RoleCreate, RoleUpdate

role_router = APIRouter(prefix="/api/iam/roles", tags=["roles"])


@role_router.get("", response_model=list[RoleBase])
def get_all_roles(role_service: RoleServiceDep):
    return role_service.get_all_roles()


@role_router.get("/{role_id}", response_model=RoleBase)
def get_role_by_id(role_id: int, role_service: RoleServiceDep):
    role = role_service.get_role_by_id(role_id)
    if role is None:
        raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")

    return role


@role_router.post("", status_code=status.HTTP_201_CREATED, response_model=RoleBase)
def create_role(role: RoleCreate, create_role_use_case: CreateRoleUseCaseDep):
    if not role.name:
        raise get_bad_request_exception("El nombre del rol es obligatorio.")
    try:
        return create_role_use_case.invoke(role)
    except IntegrityError:
        raise get_conflict_exception(f"Ya existe un rol con el nombre '{role.name}'.")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error al guardar un rol: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )


@role_router.put("/{role_id}", response_model=RoleBase)
def update_role(role_id: int, role: RoleUpdate, update_role_use_case: UpdateRoleUseCaseDep):
    if not role.name and not role.description and role.modules is None:
        raise get_bad_request_exception(
            "Debes enviar al menos un campo para actualizar."
        )
    try:
        return update_role_use_case.invoke(role_id, role)
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
