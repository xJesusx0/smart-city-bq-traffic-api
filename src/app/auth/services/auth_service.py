from src.app.core.models.user import UserBase, DbUser
from src.app.core.security.encryption_service import verify


class AuthService:

    def authenticate_user(self, username: str, password: str) -> UserBase | None:
        user = self.find_by_username(username)
        if not user:
            return None

        if verify(password, user.password):
            return user
        return None


    def find_by_username(self, username: str) -> UserBase | None:
        if username == "jesus@foo.var":
            return DbUser(

            )

        return None