from app.core.models.user import (
    UserBase,
    UserCreate,
    UserCreateWithPassword,
    UserUpdate,
)
from app.core.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_all_users(self, active: bool | None = None) -> list[UserBase]:
        if active is None:
            db_users = self.user_repository.get_all_users()
        else:
            db_users = self.user_repository.get_all_users_by_active(active=active)
        return [UserBase.map_from_db(db_user) for db_user in db_users]

    def get_user_by_id(self, user_id: int) -> UserBase | None:
        db_user = self.user_repository.get_user_by_id(user_id)
        if db_user:
            return UserBase.map_from_db(db_user)
        return None

    def create_user(self, user: UserCreate) -> UserBase:
        user_with_password = UserCreateWithPassword(**user.model_dump(), password="")
        db_user = self.user_repository.create_user(user_with_password)
        return UserBase.map_from_db(db_user)

    def update_user(self, user_id: int, user: UserUpdate) -> UserBase | None:
        db_user = self.user_repository.update_user(user_id, user)
        if db_user:
            return UserBase.map_from_db(db_user)
        return None

    def delete_user(self, user_id: int) -> UserBase | None:
        db_user = self.user_repository.delete_user_by_id(user_id)
        if db_user:
            return UserBase.map_from_db(db_user)
        return None
