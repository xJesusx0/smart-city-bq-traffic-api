from sqlmodel import Session, select

from app.core.models.module_role import DbModuleRole
from app.core.repositories.module_role_repository import ModuleRoleRepository


class ModuleRoleRepositoryImpl(ModuleRoleRepository):
    def __init__(self, session: Session):
        self.session = session

    def assign_modules_to_role(self, role_id: int, module_ids: list[int]) -> None:
        new_module_roles = [
            DbModuleRole(role_id=role_id, module_id=module_id)
            for module_id in module_ids
        ]

        self.session.add_all(new_module_roles)
        self.session.commit()

    def sync_modules_for_role(self, role_id: int, module_ids: list[int]) -> None:
        current_module_roles = self.session.exec(
            select(DbModuleRole).where(DbModuleRole.role_id == role_id)
        ).all()

        current_modules_map = {mr.module_id: mr for mr in current_module_roles}
        new_module_ids_set = set(module_ids)

        # Deactivate module roles that are no longer assigned
        for module_id, module_role in current_modules_map.items():
            if module_id not in new_module_ids_set and module_role.active:
                module_role.active = False
                self.session.add(module_role)

        # Activate existing module roles or create new ones
        for module_id in new_module_ids_set:
            module_role = current_modules_map.get(module_id)
            if module_role:
                if not module_role.active:
                    module_role.active = True
                    self.session.add(module_role)
            else:
                new_module_role = DbModuleRole(role_id=role_id, module_id=module_id)
                self.session.add(new_module_role)

        self.session.commit()
