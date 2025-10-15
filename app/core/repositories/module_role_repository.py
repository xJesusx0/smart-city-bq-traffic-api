from abc import ABC, abstractmethod


class ModuleRoleRepository(ABC):
    @abstractmethod
    def assign_modules_to_role(self, role_id: int, module_ids: list[int]) -> None:
        """
        Assigns multiple modules to a role.
        """
        pass

    @abstractmethod
    def sync_modules_for_role(self, role_id: int, module_ids: list[int]) -> None:
        """
        Synchronizes the modules of a role with the given list of module IDs.
        """
        pass
