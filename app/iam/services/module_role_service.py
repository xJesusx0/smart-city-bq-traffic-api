from app.core.repositories.module_role_repository import ModuleRoleRepository


class ModuleRoleService:
    def __init__(self, module_role_repository: ModuleRoleRepository):
        self.module_role_repository = module_role_repository

    def assign_modules_to_role(self, role_id: int, module_ids: list[int]) -> None:
        """
        Assigns multiple modules to a role.
        """
        self.module_role_repository.assign_modules_to_role(role_id, module_ids)

    def sync_modules_for_role(self, role_id: int, module_ids: list[int]) -> None:
        """
        Synchronizes the modules of a role with the given list of module IDs.
        """
        self.module_role_repository.sync_modules_for_role(role_id, module_ids)
