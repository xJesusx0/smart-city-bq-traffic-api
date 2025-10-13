import traceback
import logging

from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.models.dtos import UserWithModulesDTO
from app.auth.models.token import Token
from app.auth.models.oauth_google import GoogleTokenRequest
from app.core.security.jwt_service import create_access_token
from app.core.dependencies import (
    AuthServiceDep,
    CurrentUserDep,
    GoogleAuthServiceDep,
    GetModulesWithUseCaseDep,
)
from app.core.exceptions import (
    get_credentials_exception,
    get_internal_server_error_exception,
)

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> Token:
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

    token = create_access_token(data={"sub": user.email})

    return Token(access_token=token, token_type="bearer")


@auth_router.post("/login/google")
def oauth_google_login(
    token_request: GoogleTokenRequest,
    auth_service: AuthServiceDep,
    google_auth_service: GoogleAuthServiceDep,
) -> Token:
    try:
        print("Validando token de Google...")
        google_user_info = google_auth_service.get_user_info(token_request.token)

        print("Token de Google validado:", google_user_info)
        if google_user_info is None:
            raise get_credentials_exception("Token de google inválido")

        user = auth_service.authenticate_google_user(google_user_info)

        if user is None:
            raise get_credentials_exception("Credenciales de autenticacion invalidas")

        token = create_access_token(data={"sub": user.email})

        return Token(access_token=token, token_type="bearer")
    except ValueError:
        print(traceback.format_exc())
        raise get_credentials_exception("No se pudo validar el token de Google")
    except Exception:
        print(traceback.format_exc())
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado al validar el token de Google"
        )


@auth_router.get("/me")
def me(
    current_user: CurrentUserDep,
    get_user_with_modules_use_case: GetModulesWithUseCaseDep,
) -> UserWithModulesDTO:
    if current_user.id is None:
        raise get_credentials_exception()

    try:
        return get_user_with_modules_use_case.invoke(current_user)

    except Exception as e:
        logging.error(str(e))
        raise get_internal_server_error_exception(
            "Ocurrio un error inesperado al obtener los modulos del usuario actal"
        )
