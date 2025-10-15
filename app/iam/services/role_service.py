from typing import Optional

from app.core.models.role import DbRole, RoleCreate, RoleUpdate
from app.core.repositories.role_repository import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def get_roles_by_user_id(self, user_id: int) -> list[DbRole]:
        """
        Gets all roles for a given user.
        """
        return self.role_repository.get_roles_by_user_id(user_id)

    def get_all_roles(self, active: bool | None = None) -> list[DbRole]:
        if active is None:
            return self.role_repository.get_all_roles()
        else:
            return self.role_repository.get_all_roles_by_active(active=active)

    def get_role_by_id(self, role_id: int) -> Optional[DbRole]:
        return self.role_repository.get_role_by_id(role_id)

    def create_role(self, role: RoleCreate) -> DbRole:
        return self.role_repository.create_role(role)

    def update_role(self, role_id: int, role: RoleUpdate) -> Optional[DbRole]:
        return self.role_repository.update_role(role_id, role)

    def delete_role(self, role_id: int) -> Optional[DbRole]:
        return self.role_repository.delete_role_by_id(role_id)

    def get_roles_by_ids(self, role_ids: list[int]) -> list[DbRole]:
        return self.role_repository.get_roles_by_ids(role_ids)

    def get_roles_map_by_user_ids(self, user_ids: list[int]) -> dict[int, list[DbRole]]:
        return self.role_repository.get_roles_by_user_ids_map(user_ids)
