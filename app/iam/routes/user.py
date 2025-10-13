import logging
import traceback

from fastapi import Response, status
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import (
    CreateUserUseCaseDep,
    UpdateUserUseCaseDep,
    UserServiceDep,
)
from app.core.exceptions import (
    get_bad_request_exception,
    get_conflict_exception,
    get_entity_not_found_exception,
    get_internal_server_error_exception,
)
from app.core.models.user import UserBase, UserCreate, UserUpdate
from app.core.validations import is_valid_email

user_router = APIRouter(prefix="/api/iam/users", tags=["users"])


@user_router.get("", response_model=list[UserBase])
def get_all_users(user_service: UserServiceDep, active: bool | None = None):
    return user_service.get_all_users(active=active)


@user_router.get("/{user_id}", response_model=UserBase)
def get_user_by_id(user_id: int, user_service: UserServiceDep):
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise get_entity_not_found_exception(f"Usuario con id {user_id} no encontrado")

    return user


@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserBase)
def create_user(user: UserCreate, create_user_use_case: CreateUserUseCaseDep):
    valid_user = _validate_user_to_create(user)
    if not valid_user:
        raise get_bad_request_exception("Datos de usuario inválidos.")
    try:
        return create_user_use_case.invoke(user)
    except IntegrityError:
        raise get_conflict_exception(
            f"Ya existe un usuario registrado con el email '{user.email}' o con el mismo numero de identificación."
        )
    except Exception as e:
        logging.error(f"Error al guardar un usuario: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )


@user_router.put("/{user_id}", response_model=UserBase)
def update_user(
    user_id: int, user: UserUpdate, update_user_use_case: UpdateUserUseCaseDep
):
    valid_user = _validate_user_to_update(user)
    if not valid_user:
        raise get_bad_request_exception("Datos de usuario inválidos.")
    try:
        return update_user_use_case.invoke(user_id, user)
    except IntegrityError:
        print(traceback.format_exc())
        raise get_conflict_exception(
            f"Ya existe un usuario registrado con el email '{user.email}' "
        )
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error al guardar un usuario: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, user_service: UserServiceDep):
    user = user_service.delete_user(user_id)
    if user is None:
        raise get_entity_not_found_exception(f"Usuario con id {user_id} no encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _validate_user_to_create(user: UserCreate):
    if not user.email or not user.name or not user.identification or not user.password:
        raise get_bad_request_exception("Todos los campos son obligatorios.")

    if not is_valid_email(user.email):
        raise get_bad_request_exception(
            "El correo electrónico no tiene un formato válido."
        )

    if len(user.password) < 8:
        raise get_bad_request_exception(
            "La contraseña debe tener al menos 8 caracteres."
        )

    if not user.identification.isdigit():
        raise get_bad_request_exception("La identificación debe contener solo números.")

    if not user.roles:
        user.roles = []
    return True


def _validate_user_to_update(user: "UserUpdate"):
    if not user.email and not user.name and user.roles is None:
        raise get_bad_request_exception(
            "Debes enviar al menos un campo para actualizar."
        )

    if user.email:
        if not is_valid_email(user.email):
            raise get_bad_request_exception(
                "El correo electrónico no tiene un formato válido."
            )

    if user.name and not user.name.strip():
        raise get_bad_request_exception("El nombre no puede estar vacío.")

    if user.roles is not None and not isinstance(user.roles, list):
        raise get_bad_request_exception("Roles debe ser una lista de números.")

    return True
