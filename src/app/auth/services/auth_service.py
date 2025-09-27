from app.auth.models.user import User
from app.core.encryption_service import verify, encrypt


class AuthService:

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self.find_by_username(username)
        if not user:
            return None

        if verify(password, user.password):
            return user
        return None


    def find_by_username(self, username: str) -> User | None:
        if username == "jesus":
            return User(username="jesus", email="jesus@foo.var", full_name="Jesus Perea", disabled=False, password=encrypt("12345"))

        return None