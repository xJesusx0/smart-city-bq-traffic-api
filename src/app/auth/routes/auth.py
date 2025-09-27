from http.client import HTTPException
from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.auth.services.auth_service import AuthService
from app.auth.models.user import User
from app.core.jwt_service import create_access_token, get_current_active_user

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

    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username})

    return JSONResponse(content={"access_token": token, "token_type": "bearer"})

@auth_router.get("/me")
def me(current_user: Annotated[User, Depends(get_current_active_user)]) -> JSONResponse:
    return JSONResponse(content={"username": current_user.username, "email": current_user.email})



