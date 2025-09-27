from http.client import HTTPException
from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from src.app.auth.services.auth_service import AuthService
from src.app.auth.models.user import User
from src.app.core.security import get_current_active_user, build_token

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()

@auth_router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> JSONResponse:

    if form_data.username is None or form_data.password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.find_by_username(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = build_token(user)

    return JSONResponse(content={"access_token": token, "token_type": "bearer"})

@auth_router.get("/me")
def me(current_user: Annotated[User, Depends(get_current_active_user)]) -> JSONResponse:
    return JSONResponse(content={"username": current_user.username, "email": current_user.email})



