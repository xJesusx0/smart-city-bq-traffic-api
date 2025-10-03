from app.core.models.role import DbRole
from app.core.repositories.role_repository import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def get_roles_by_user_id(self, user_id: int) -> list[DbRole]:
        """
        Gets all roles for a given user.
        """
        return self.role_repository.get_roles_by_user_id(user_id)
