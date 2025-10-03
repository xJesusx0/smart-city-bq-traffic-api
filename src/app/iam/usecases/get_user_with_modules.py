from app.core.models.user import UserBase
from app.iam.services.user_service import UserService
from app.iam.dtos.user import UserWithModulesDTO
from app.iam.services.module_service import ModuleService
from app.iam.services.role_service import RoleService


class GetUserWithModulesUseCase:
    """
    Use case to retrieve a user's details along with all the modules they have access to
    through their assigned roles.
    """

    def __init__(
        self,
        user_service: UserService,
        module_service: ModuleService,
        role_service: RoleService,
    ):
        self.user_service = user_service
        self.module_service = module_service
        self.role_service = role_service

    def invoke(self, user: UserBase) -> UserWithModulesDTO:
        roles = self.role_service.get_roles_by_user_id(user.id)

        role_ids = [role.id for role in roles]
        modules = self.module_service.get_modules_by_role_ids(role_ids)

        return UserWithModulesDTO(modules=modules, **user.model_dump())
