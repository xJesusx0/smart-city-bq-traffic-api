from app.core.models.user import UserBase
from app.core.models.module import ModuleBase
from app.core.models.role import RoleBase
from app.auth.models.dtos import UserWithModulesDTO
from app.iam.services.user_service import UserService
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
        if user.id is None:
            raise ValueError("User ID cannot be None")

        roles = self.role_service.get_roles_by_user_id(user.id)
        if not roles:
            return UserWithModulesDTO(modules=[], **user.model_dump())

        role_ids = [role.id for role in roles if role.id is not None]
        if not role_ids:
            return UserWithModulesDTO(modules=[], **user.model_dump())

        modules = self.module_service.get_modules_by_role_ids(role_ids)
        modules = [ModuleBase.model_validate(module) for module in modules]
        roles = [RoleBase.model_validate(role) for role in roles]

        return UserWithModulesDTO(modules=modules, roles=roles, **user.model_dump())
