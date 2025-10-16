import logging
import traceback

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import (
    CreateRoleUseCaseDep,
    GetRolesWithModulesUseCaseDep,
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
from app.iam.dtos.role_with_modules import RoleWithModulesDTO

role_router = APIRouter(prefix="/api/iam/roles", tags=["roles"])


@role_router.get("", response_model=list[RoleBase])
def get_all_roles(role_service: RoleServiceDep, active: bool | None = None):
    return role_service.get_all_roles(active=active)


@role_router.get("/{role_id:int}", response_model=RoleBase)
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


@role_router.put("/{role_id:int}", response_model=RoleBase)
def update_role(
    role_id: int, role: RoleUpdate, update_role_use_case: UpdateRoleUseCaseDep
):
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


@role_router.delete("/{role_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, role_service: RoleServiceDep):
    role = role_service.delete_role(role_id)
    if role is None:
        raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@role_router.get("/with-modules", response_model=list[RoleWithModulesDTO])
def get_all_roles_with_modules(
    get_roles_with_modules_use_case: GetRolesWithModulesUseCaseDep,
    active: bool | None = None,
):
    print("get_all_roles_with_modules")
    try:
        return get_roles_with_modules_use_case.invoke(active=active)
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error al obtener los roles con modulos: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )
