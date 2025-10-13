from datetime import datetime, timedelta, timezone

import jwt

from app.core.settings import settings

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
