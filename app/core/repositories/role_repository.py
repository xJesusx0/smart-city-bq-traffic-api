from abc import ABC, abstractmethod
from app.core.models.role import DbRole


class RoleRepository(ABC):
    @abstractmethod
    def get_roles_by_user_id(self, user_id: int) -> list[DbRole]:
        """
        Retrieves all roles associated with a given user ID.
        """
        pass
