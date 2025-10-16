from collections import defaultdict

from app.core.models.module import DbModule
from app.core.repositories.module_repository import ModuleRepository
from app.core.repositories.module_role_repository import ModuleRoleRepository


class ModuleService:
    def __init__(
        self,
        module_repository: ModuleRepository,
        module_role_repository: ModuleRoleRepository | None = None,
    ):
        self.module_repository = module_repository
        self.module_role_repository = module_role_repository

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

    def get_modules_map_by_role_ids(
        self, role_ids: list[int]
    ) -> dict[int, list[DbModule]]:
        if not role_ids or self.module_role_repository is None:
            return {}

        role_to_module_ids = self.module_role_repository.get_module_ids_map_by_role_ids(
            role_ids
        )
        all_module_ids = {mid for mids in role_to_module_ids.values() for mid in mids}
        if not all_module_ids:
            return {rid: [] for rid in role_ids}

        modules = self.get_modules_by_ids(list(all_module_ids))
        modules = [
            module for module in modules if module.id is not None and module.active
        ]
        module_by_id = {m.id: m for m in modules if m.id is not None}

        result: dict[int, list[DbModule]] = defaultdict(list)
        for role_id, mids in role_to_module_ids.items():
            result[role_id] = [module_by_id[mid] for mid in mids if mid in module_by_id]

        # Ensure every requested role_id is present in the map
        for rid in role_ids:
            result.setdefault(rid, [])

        return dict(result)
