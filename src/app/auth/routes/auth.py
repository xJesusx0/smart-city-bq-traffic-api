from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from src.app.auth.models.token import Token
from src.app.auth.services.auth_service import AuthService
from src.app.core.database.connection import get_user_repository
from src.app.core.models.user import UserBase
from src.app.core.repositories.user_repository import UserRepository
from src.app.core.security.jwt_service import create_access_token, get_current_active_user

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(user_repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(user_repository=user_repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@auth_router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthServiceDep) -> Token:
    if form_data.username is None or form_data.password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.login_name})

    return Token(access_token=token, token_type="bearer").model_dump()


@auth_router.get("/me")
def me(current_user: Annotated[UserBase, Depends(get_current_active_user)]) -> JSONResponse:
    return JSONResponse(content={"username": current_user.login_name, "email": current_user.login_name})
