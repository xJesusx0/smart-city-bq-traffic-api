from abc import ABC, abstractmethod

from app.core.models.module import DbModule


class ModuleRepository(ABC):
    @abstractmethod
    def get_modules_by_role_ids(self, role_ids: list[int]) -> list[DbModule]:
        """
        Retrieves all unique modules associated with a given list of role IDs.
        """
        pass

    @abstractmethod
    def get_modules_by_ids(self, module_ids: list[int]) -> list[DbModule]:
        """
        Retrieves a list of modules based on a list of module IDs.
        """
        pass

    @abstractmethod
    def get_all_modules(self) -> list[DbModule]:
        """
        Retrieves all modules.
        """
        pass

    @abstractmethod
    def get_all_modules_by_active(self, active: bool) -> list[DbModule]:
        """
        Retrieves all modules by active status.
        """
        pass

    @abstractmethod
    def get_module_by_id(self, module_id: int) -> DbModule | None:
        """
        Retrieves a module by its ID.
        """
        pass
