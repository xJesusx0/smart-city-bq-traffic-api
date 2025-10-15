from abc import ABC, abstractmethod
from typing import Optional

from app.core.models.role import DbRole, RoleCreate, RoleUpdate


class RoleRepository(ABC):
    @abstractmethod
    def get_roles_by_user_id(self, user_id: int) -> list[DbRole]:
        """
        Retrieves all roles associated with a given user ID.
        """
        pass

    @abstractmethod
    def get_all_roles(self) -> list[DbRole]:
        pass

    @abstractmethod
    def get_all_roles_by_active(self, active: bool) -> list[DbRole]:
        pass

    @abstractmethod
    def get_role_by_id(self, role_id: int) -> Optional[DbRole]:
        pass

    @abstractmethod
    def create_role(self, role: RoleCreate) -> DbRole:
        pass

    @abstractmethod
    def update_role(self, role_id: int, role: RoleUpdate) -> Optional[DbRole]:
        pass

    @abstractmethod
    def delete_role_by_id(self, role_id: int) -> Optional[DbRole]:
        pass

    @abstractmethod
    def get_roles_by_ids(self, role_ids: list[int]) -> list[DbRole]:
        pass

    @abstractmethod
    def get_roles_by_user_ids_map(self, user_ids: list[int]) -> dict[int, list[DbRole]]:
        """
        Returns a mapping from user_id to the list of roles assigned to that user.
        Users without roles should not appear in the map or map to an empty list.
        """
        pass
