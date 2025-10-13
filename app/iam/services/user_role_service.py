from app.core.repositories.user_role_repository import UserRoleRepository


class UserRoleService:
    def __init__(self, user_role_repository: UserRoleRepository):
        self.user_role_repository = user_role_repository

    def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        """
        Assigns a role to a user.
        """
        self.user_role_repository.assign_role_to_user(user_id, role_id)

    def remove_role_from_user(self, user_id: int, role_id: int) -> None:
        """
        Removes a role from a user.
        """
        self.user_role_repository.remove_role_from_user(user_id, role_id)

    def assign_roles_to_user(self, user_id: int, role_ids: list[int]) -> None:
        """
        Assigns multiple roles to a user.
        """
        self.user_role_repository.assign_roles_to_user(user_id, role_ids)

    def remove_all_roles_from_user(self, user_id: int) -> None:
        """
        Removes all roles from a user.
        """
        self.user_role_repository.remove_all_roles_from_user(user_id)
