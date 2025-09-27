from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import HTTPException, status
from fastapi.params import Depends
from jwt import InvalidTokenError


from app.core.models.user import DbUser, UserBase
from app.auth.services.auth_service import AuthService
from app.core.settings import settings
from app.core.security.security import oauth2_scheme
from app.core.database.connection import UserRepoDep

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_DAYS = settings.jwt_expiration_time


def __get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_repository: UserRepoDep) -> DbUser:
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


def get_current_active_user(current_user: Annotated[DbUser, Depends(__get_current_user)]) -> DbUser:
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_access_token(data: dict):
    to_encode = data.copy()

    expiration_days = ACCESS_TOKEN_EXPIRE_DAYS
    expires_delta = timedelta(days=expiration_days)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt