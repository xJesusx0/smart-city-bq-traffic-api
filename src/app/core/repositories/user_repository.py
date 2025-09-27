from abc import ABC, abstractmethod

class UserRepository(ABC):

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    def get_user_by_login_name(self, login_name: str):
        pass