from app.auth.models.oauth import MicrosoftUserInfo
import requests
from jwt import PyJWKClient, decode

class MicrosoftAuthService:
    def __init__(self, client_id: str, tenant_id: str):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        self.issuer =  f"https://login.microsoftonline.com/{tenant_id}/v2.0"

    def get_user_info(self, token: str) -> MicrosoftUserInfo:
        jwk_client = PyJWKClient(self.jwks_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        # Decodifica y valida
        payload = decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.client_id,
            issuer=self.issuer,
        )

        microsoft_user_info = {
            "email": payload.get("preferred_username"),
            "name": payload.get("name"),
        }

        return MicrosoftUserInfo(**microsoft_user_info)

        