from app.core.models.user import UserBase, DbUser
from app.core.repositories.user_repository import UserRepository
from app.core.security.encryption_service import verify


class AuthService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str) -> DbUser | None:
        user = self.user_repository.get_user_by_login_name(username)
        if not user:
            return None

        if verify(password, user.password):
            return user
        return None