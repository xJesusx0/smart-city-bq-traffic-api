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
