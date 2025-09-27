from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt

from fastapi.params import Depends
from fastapi import HTTPException, status
from jwt import InvalidTokenError


from src.app.core.models.user import UserBase
from src.app.auth.services.auth_service import AuthService
from src.app.core.settings import settings
from src.app.core.security import oauth2_scheme

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_DAYS = settings.jwt_expiration_time
auth_service = AuthService()


def decode_token(token: str) -> UserBase | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

    except InvalidTokenError as e:
        print(str(e))  # Mensaje de la excepción
        raise credentials_exception

    user = auth_service.find_by_username(username)
    if user is None:
        raise credentials_exception

    return user

def __get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserBase:
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: Annotated[UserBase, Depends(__get_current_user)],) -> UserBase:
    if current_user.active == False:
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