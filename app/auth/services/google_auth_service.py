import traceback

from google.oauth2 import id_token
from google.auth.transport import requests

from app.auth.models.oauth_google import GoogleUserInfo
from app.core.exceptions import get_credentials_exception


class GoogleAuthService:
    def __init__(self, client_id: str):
        self.client_id = client_id

    def _validate_token(self, token: str) -> dict | None:
        try:
            id_info = id_token.verify_oauth2_token(
                token, requests.Request(), self.client_id
            )

            if id_info["aud"] != self.client_id:
                raise get_credentials_exception("Token de google inválido")

            return id_info
        except ValueError:
            print(traceback.format_exc())
            raise get_credentials_exception("Token de google inválido")

    def get_user_info(self, token: str) -> GoogleUserInfo:
        try:
            id_info = self._validate_token(token)
            if id_info is None:
                raise get_credentials_exception("No se pudo validar el token de Google")

            user_info = {
                "email": id_info.get("email"),
                "name": id_info.get("name"),
                "picture": id_info.get("picture"),
                "sub": id_info.get("sub"),
            }

            return GoogleUserInfo(**user_info)
        except Exception:
            print(traceback.format_exc())
            raise get_credentials_exception("No se pudo validar el token de Google")
