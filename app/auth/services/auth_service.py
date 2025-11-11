import traceback

from app.auth.models.oauth_google import GoogleUserInfo
from app.core.models.user import DbUser
from app.core.repositories.user_repository import UserRepository
from app.core.security.encryption_service import verify


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str) -> DbUser | None:
        user = self.user_repository.get_user_by_email(username)
        if not user or not user.active:
            return None

        if not user.password or not user.password.strip():
            return None

        if user.must_change_password:
            return None

        if verify(password, user.password):
            return user
        return None

    def authenticate_google_user(
        self, google_user_info: GoogleUserInfo
    ) -> DbUser | None:
        try:
            if not google_user_info.email:
                return None

            user = self.user_repository.get_user_by_email(google_user_info.email)

            return user
        except Exception:
            print(traceback.format_exc())
            return None
