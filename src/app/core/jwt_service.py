from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt

from fastapi.params import Depends
from fastapi import HTTPException, status
from jwt import InvalidTokenError


from app.auth.models.user import User
from app.auth.services.auth_service import AuthService
from app.core.settings import settings
from app.core.security import oauth2_scheme

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_DAYS = settings.jwt_expiration_time
auth_service = AuthService()


def decode_token(token: str) -> User | None:
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

    except InvalidTokenError:
        raise credentials_exception

    user = auth_service.find_by_username(username)
    if user is None:
        raise credentials_exception

    return user

def __get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: Annotated[User, Depends(__get_current_user)],) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def build_token(user: User) -> str:
    return user.username

def create_access_token(data: dict):
    to_encode = data.copy()

    expiration_days = ACCESS_TOKEN_EXPIRE_DAYS
    expires_delta = timedelta(days=expiration_days)


    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt