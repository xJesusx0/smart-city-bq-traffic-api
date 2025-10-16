from app.core.exceptions import get_bad_request_exception
from app.core.models.role import RoleBase, RoleCreate
from app.iam.services.module_role_service import ModuleRoleService
from app.iam.services.module_service import ModuleService
from app.iam.services.role_service import RoleService


class CreateRoleUseCase:
    def __init__(
        self,
        role_service: RoleService,
        module_service: ModuleService,
        module_role_service: ModuleRoleService,
    ):
        self.role_service = role_service
        self.module_service = module_service
        self.module_role_service = module_role_service

    def invoke(self, role_to_create: RoleCreate) -> RoleBase:
        # Validate modules
        if role_to_create.modules:
            modules = self.module_service.get_modules_by_ids(role_to_create.modules)
            if len(modules) != len(role_to_create.modules):
                raise get_bad_request_exception(
                    "Uno o mas de los modulos seleccionados son invalidos."
                )

        # Create role
        created_role = self.role_service.create_role(role_to_create)
        if not created_role or not created_role.id:
            raise get_bad_request_exception("No se pudo crear el rol.")

        # Assign modules to role
        if role_to_create.modules:
            self.module_role_service.assign_modules_to_role(
                created_role.id, role_to_create.modules
            )

        return created_role
