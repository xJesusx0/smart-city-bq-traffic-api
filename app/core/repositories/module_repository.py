from abc import ABC, abstractmethod
from app.core.models.module import DbModule


class ModuleRepository(ABC):
    @abstractmethod
    def get_modules_by_role_ids(self, role_ids: list[int]) -> list[DbModule]:
        """
        Retrieves all unique modules associated with a given list of role IDs.
        """
        pass
