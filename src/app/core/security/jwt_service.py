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

JWT_SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_DAYS = settings.jwt_expiration_time

def create_access_token(data: dict):
    to_encode = data.copy()

    expiration_days = ACCESS_TOKEN_EXPIRE_DAYS
    expires_delta = timedelta(days=expiration_days)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt