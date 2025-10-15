from app.core.models.module import DbModule
from app.core.repositories.module_repository import ModuleRepository


class ModuleService:
    def __init__(self, module_repository: ModuleRepository):
        self.module_repository = module_repository

    def get_modules_by_role_ids(self, role_ids: list[int]) -> list[DbModule]:
        """
        Gets all modules associated with a list of role IDs.
        """
        modules = self.module_repository.get_modules_by_role_ids(role_ids)
        print(modules)
        return modules

    def get_modules_by_ids(self, module_ids: list[int]) -> list[DbModule]:
        """
        Gets all modules by a list of IDs.
        """
        return self.module_repository.get_modules_by_ids(module_ids)

    def get_all_modules(self, active: bool | None = None) -> list[DbModule]:
        """
        Gets all modules.
        """
        if active is None:
            return self.module_repository.get_all_modules()
        else:
            return self.module_repository.get_all_modules_by_active(active=active)

    def get_module_by_id(self, module_id: int) -> DbModule | None:
        """
        Gets a module by its ID.
        """
        return self.module_repository.get_module_by_id(module_id)
