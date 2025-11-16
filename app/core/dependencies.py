import traceback
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException
from fastapi_mail import ConnectionConfig
from jwt import InvalidTokenError

from app.auth.services.auth_service import AuthService
from app.auth.services.google_auth_service import GoogleAuthService
from app.core.database.connection import SessionDep
from app.core.database.mongo.mongo import MongoDB, mongodb
from app.core.database.repositories.location_repository_impl import (
    LocationRepositoryImpl,
)
from app.core.database.repositories.module_repository_impl import ModuleRepositoryImpl
from app.core.database.repositories.module_role_repository_impl import (
    ModuleRoleRepositoryImpl,
)
from app.core.database.repositories.role_repository_impl import RoleRepositoryImpl
from app.core.database.repositories.user_repository_impl import UserRepositoryImpl
from app.core.database.repositories.user_role_repository_impl import (
    UserRoleRepositoryImpl,
)
from app.core.email.services.email_service import EmailService
from app.core.exceptions import get_credentials_exception
from app.core.models.user import DbUser
from app.core.repositories.location_repository import LocationRepository
from app.core.repositories.module_repository import ModuleRepository
from app.core.repositories.module_role_repository import ModuleRoleRepository
from app.core.repositories.role_repository import RoleRepository
from app.core.repositories.user_repository import UserRepository
from app.core.repositories.user_role_repository import UserRoleRepository
from app.core.security.security import oauth2_scheme
from app.core.settings import email_settings, settings
from app.geo.services.geo_info_service import GeoInfoService
from app.iam.services.module_role_service import ModuleRoleService
from app.iam.services.module_service import ModuleService
from app.iam.services.role_service import RoleService
from app.iam.services.user_role_service import UserRoleService
from app.iam.services.user_service import UserService
from app.iam.usecases.create_role import CreateRoleUseCase
from app.iam.usecases.create_user import CreateUserUseCase
from app.iam.usecases.get_roles_with_modules import GetRolesWithModulesUseCase
from app.iam.usecases.get_user_with_modules import GetUserWithModulesUseCase
from app.iam.usecases.get_users_with_roles import GetUsersWithRolesUseCase
from app.iam.usecases.update_role import UpdateRoleUseCase
from app.iam.usecases.update_user import UpdateUserUseCase
from app.traffic.services.location_service import LocationService

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_DAYS = settings.jwt_expiration_time


# --- Repositories


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepositoryImpl(session=session)


def get_module_repository(session: SessionDep) -> ModuleRepository:
    return ModuleRepositoryImpl(session)


def get_role_repository(session: SessionDep) -> RoleRepository:
    return RoleRepositoryImpl(session)


def get_user_role_repository(session: SessionDep) -> UserRoleRepository:
    return UserRoleRepositoryImpl(session=session)


def get_module_role_repository(session: SessionDep) -> ModuleRoleRepository:
    return ModuleRoleRepositoryImpl(session)


def get_location_repository(session: SessionDep) -> LocationRepository:
    return LocationRepositoryImpl(session)


async def get_mongo_db() -> MongoDB:
    await mongodb.ensure_connection()
    return mongodb


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
ModuleRepoDep = Annotated[ModuleRepository, Depends(get_module_repository)]
RoleRepoDeb = Annotated[RoleRepository, Depends(get_role_repository)]
UserRoleRepoDep = Annotated[UserRoleRepository, Depends(get_user_role_repository)]
ModuleRoleRepoDep = Annotated[ModuleRoleRepository, Depends(get_module_role_repository)]
LocationRepoDep = Annotated[LocationRepository, Depends(get_location_repository)]

MongoDBDep = Annotated[MongoDB, Depends(get_mongo_db)]
# --- Services


def get_google_auth_service() -> GoogleAuthService:
    return GoogleAuthService(client_id=settings.google_client_id)


def get_auth_service(user_repository: UserRepoDep) -> AuthService:
    return AuthService(user_repository=user_repository)


def get_user_service(user_repository: UserRepoDep) -> UserService:
    return UserService(user_repository=user_repository)


def get_module_service(
    module_repository: ModuleRepoDep, module_role_repository: ModuleRoleRepoDep
) -> ModuleService:
    return ModuleService(
        module_repository=module_repository,
        module_role_repository=module_role_repository,
    )


def get_role_service(role_repository: RoleRepoDeb) -> RoleService:
    return RoleService(role_repository=role_repository)


def get_user_role_service(user_role_repository: UserRoleRepoDep) -> UserRoleService:
    return UserRoleService(user_role_repository=user_role_repository)


def get_module_role_service(
    module_role_repository: ModuleRoleRepoDep,
) -> ModuleRoleService:
    return ModuleRoleService(module_role_repository=module_role_repository)


def get_location_service(location_repository: LocationRepoDep) -> LocationService:
    return LocationService(location_repository=location_repository)


def get_email_service() -> EmailService:
    return EmailService(ConnectionConfig(**email_settings.model_dump()))


def get_geo_info_service() -> GeoInfoService:
    return GeoInfoService(base_url=settings.geo_info_service_url)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ModuleServiceDep = Annotated[ModuleService, Depends(get_module_service)]
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
UserRoleServiceDep = Annotated[UserRoleService, Depends(get_user_role_service)]
ModuleRoleServiceDep = Annotated[ModuleRoleService, Depends(get_module_role_service)]
LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]
GoogleAuthServiceDep = Annotated[GoogleAuthService, Depends(get_google_auth_service)]
EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
GeoInfoServiceDep = Annotated[GeoInfoService, Depends(get_geo_info_service)]


# --- Usecases
def get_get_user_with_modules_use_case(
    user_service: UserServiceDep,
    module_service: ModuleServiceDep,
    role_service: RoleServiceDep,
) -> GetUserWithModulesUseCase:
    return GetUserWithModulesUseCase(user_service, module_service, role_service)


def get_get_users_with_roles_use_case(
    user_service: UserServiceDep,
    role_service: RoleServiceDep,
) -> GetUsersWithRolesUseCase:
    return GetUsersWithRolesUseCase(user_service, role_service)


def get_create_user_use_case(
    user_service: UserServiceDep,
    role_service: RoleServiceDep,
    user_role_service: UserRoleServiceDep,
) -> CreateUserUseCase:
    return CreateUserUseCase(user_service, role_service, user_role_service)


def get_update_user_use_case(
    user_service: UserServiceDep,
    role_service: RoleServiceDep,
    user_role_service: UserRoleServiceDep,
) -> UpdateUserUseCase:
    return UpdateUserUseCase(user_service, role_service, user_role_service)


def get_create_role_use_case(
    role_service: RoleServiceDep,
    module_service: ModuleServiceDep,
    module_role_service: ModuleRoleServiceDep,
) -> CreateRoleUseCase:
    return CreateRoleUseCase(role_service, module_service, module_role_service)


def get_update_role_use_case(
    role_service: RoleServiceDep,
    module_service: ModuleServiceDep,
    module_role_service: ModuleRoleServiceDep,
) -> UpdateRoleUseCase:
    return UpdateRoleUseCase(role_service, module_service, module_role_service)


def get_get_roles_with_modules_use_case(
    role_service: RoleServiceDep,
    module_service: ModuleServiceDep,
) -> GetRolesWithModulesUseCase:
    return GetRolesWithModulesUseCase(role_service, module_service)


GetModulesWithUseCaseDep = Annotated[
    GetUserWithModulesUseCase, Depends(get_get_user_with_modules_use_case)
]
GetUsersWithRolesUseCaseDep = Annotated[
    GetUsersWithRolesUseCase, Depends(get_get_users_with_roles_use_case)
]
GetRolesWithModulesUseCaseDep = Annotated[
    GetRolesWithModulesUseCase, Depends(get_get_roles_with_modules_use_case)
]
CreateUserUseCaseDep = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]
UpdateUserUseCaseDep = Annotated[UpdateUserUseCase, Depends(get_update_user_use_case)]
CreateRoleUseCaseDep = Annotated[CreateRoleUseCase, Depends(get_create_role_use_case)]
UpdateRoleUseCaseDep = Annotated[UpdateRoleUseCase, Depends(get_update_role_use_case)]

# --- Security


def validate_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise get_credentials_exception()

        return payload
    except InvalidTokenError:
        print(traceback.format_exc())
        raise get_credentials_exception("Token invalido")


ValidTokenDep = Annotated[dict[str, Any], Depends(validate_token)]


def get_current_user(payload: ValidTokenDep, user_repository: UserRepoDep) -> DbUser:
    username: str | None = payload.get("sub")
    if username is None:
        raise get_credentials_exception()

    user = user_repository.get_user_by_email(username)
    if user is None:
        raise get_credentials_exception()

    return user


CurrentUserDep = Annotated[DbUser, Depends(get_current_user)]


def get_current_active_user(current_user: CurrentUserDep) -> DbUser:
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
