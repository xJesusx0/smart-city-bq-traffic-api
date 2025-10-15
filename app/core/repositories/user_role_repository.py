from abc import ABC, abstractmethod


class UserRoleRepository(ABC):
    @abstractmethod
    def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        """
        Assigns a role to a user.
        """
        pass

    @abstractmethod
    def remove_role_from_user(self, user_id: int, role_id: int) -> None:
        """
        Removes a role from a user.
        """
        pass

    @abstractmethod
    def assign_roles_to_user(self, user_id: int, role_ids: list[int]) -> None:
        """
        Assigns multiple roles to a user.
        """
        pass

    @abstractmethod
    def remove_all_roles_from_user(self, user_id: int) -> None:
        """
        Removes all roles from a user.
        """
        pass
