from app.iam.services.user_service import UserService
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt import InvalidTokenError

from app.auth.services.auth_service import AuthService
from app.core.database.connection import SessionDep
from app.core.database.repositories.user_repository_impl import UserRepositoryImpl
from app.core.models.user import DbUser
from app.core.repositories.user_repository import UserRepository
from app.core.security.security import oauth2_scheme
from app.core.settings import settings

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_DAYS = settings.jwt_expiration_time

# --- Repositories


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepositoryImpl(session=session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]

# --- Services


def get_auth_service(
    user_repository: UserRepoDep,
) -> AuthService:
    return AuthService(user_repository=user_repository)


def get_user_service(
    user_repository: UserRepoDep,
) -> UserService:
    return UserService(user_repository=user_repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
# --- Security


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], user_repository: UserRepoDep
) -> DbUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = user_repository.get_user_by_login_name(username)
    if user is None:
        raise credentials_exception

    return user


CurrentUserDep = Annotated[DbUser, Depends(get_current_user)]


def get_current_active_user(current_user: CurrentUserDep) -> DbUser:
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
