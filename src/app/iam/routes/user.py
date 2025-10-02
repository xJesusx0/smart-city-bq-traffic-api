from app.core.exceptions import get_internal_server_error_exception
from app.core.exceptions import get_conflict_exception
from sqlalchemy.exc import IntegrityError
from fastapi import status, Response

from app.core.exceptions import get_entity_not_found_exception
from app.core.models.user import UserBase, UserCreate, UserUpdate
from fastapi.routing import APIRouter

from app.core.dependencies import UserServiceDep
import logging

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
def create_user(user: UserCreate, user_service: UserServiceDep):
    try:
        return user_service.create_user(user)
    except IntegrityError:
        raise get_conflict_exception(
            f"Ya existe un usuario registrado con el login_name '{user.login_name}' "
            f"o con la identificación '{user.identification}'."
        )
    except Exception as e:
        logging.error(f"Error al guardar un usuario: {e}")
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado, contacte con un administrador"
        )


@user_router.put("/{user_id}", response_model=UserBase)
def update_user(user_id: int, user: UserUpdate, user_service: UserServiceDep):
    try:
        updated_user = user_service.update_user(user_id, user)
        if updated_user is None:
            raise get_entity_not_found_exception(
                f"Usuario con id {user_id} no encontrado"
            )
        return updated_user
    except IntegrityError:
        raise get_conflict_exception(
            f"Ya existe un usuario registrado con el login_name '{user.login_name}' "
        )
    except Exception as e:
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
