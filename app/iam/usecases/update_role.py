from app.core.exceptions import (
    get_bad_request_exception,
    get_entity_not_found_exception,
)
from app.core.models.role import RoleBase, RoleUpdate
from app.iam.services.module_role_service import ModuleRoleService
from app.iam.services.module_service import ModuleService
from app.iam.services.role_service import RoleService


class UpdateRoleUseCase:
    def __init__(
        self,
        role_service: RoleService,
        module_service: ModuleService,
        module_role_service: ModuleRoleService,
    ):
        self.role_service = role_service
        self.module_service = module_service
        self.module_role_service = module_role_service

    def invoke(self, role_id: int, role_to_update: RoleUpdate) -> RoleBase:
        # Validate role exists
        role = self.role_service.get_role_by_id(role_id)
        if not role:
            raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")

        # Validate modules if provided
        if role_to_update.modules is not None:
            modules = self.module_service.get_modules_by_ids(role_to_update.modules)
            if len(modules) != len(role_to_update.modules):
                raise get_bad_request_exception(
                    "Uno o mas de los modulos seleccionados son invalidos."
                )

        # Update role
        updated_role = self.role_service.update_role(role_id, role_to_update)
        if not updated_role:
            raise get_entity_not_found_exception(
                f"No se pudo actualizar el rol con id {role_id}"
            )

        # Sync modules
        if role_to_update.modules is not None:
            self.module_role_service.sync_modules_for_role(
                role_id, role_to_update.modules
            )

        updated_role = self.role_service.get_role_by_id(role_id)
        if not updated_role:
            raise get_entity_not_found_exception(f"Rol con id {role_id} no encontrado")

        return updated_role
