from typing import Annotated

import bcrypt

from fastapi.params import Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.app.auth.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def encrypt(data: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(data.encode("utf-8"), salt).decode("utf-8")

def verify(raw: str, encrypted: str) -> bool:
    return bcrypt.checkpw(raw.encode('utf-8'), encrypted.encode('utf-8'))

def fake_decode_token(token: str) -> User | None:
    if token == "jesus":
        return User(username="jesus", email="foo")
    return None

def __get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user = fake_decode_token(token)
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