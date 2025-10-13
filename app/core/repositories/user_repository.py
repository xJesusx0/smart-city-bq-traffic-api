from app.core.models.user import UserCreate, UserUpdate
from typing import Optional
from app.core.models.user import DbUser
from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    def get_all_users(self) -> list[DbUser]:
        pass

    @abstractmethod
    def get_all_users_by_active(self, active: bool) -> list[DbUser]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[DbUser]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[DbUser]:
        pass

    @abstractmethod
    def delete_user_by_id(self, user_id: int) -> Optional[DbUser]:
        pass

    @abstractmethod
    def create_user(self, user: UserCreate) -> DbUser:
        pass

    @abstractmethod
    def update_user(self, user_id: int, user: UserUpdate) -> Optional[DbUser]:
        pass
