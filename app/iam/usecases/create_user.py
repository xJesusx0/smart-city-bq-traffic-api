from app.iam.services.user_role_service import UserRoleService
from app.iam.services.user_service import UserService
from app.iam.services.role_service import RoleService
from app.core.models.user import UserCreate, DbUser, UserBase
from app.core.exceptions import get_bad_request_exception


class CreateUserUseCase:
    def __init__(
        self,
        user_service: UserService,
        role_service: RoleService,
        user_role_service: UserRoleService,
    ):
        self.user_service = user_service
        self.role_service = role_service
        self.user_role_service = user_role_service

    def invoke(self, user_to_create: UserCreate) -> UserBase:
        # Validate roles
        roles = self.role_service.get_roles_by_ids(user_to_create.roles)
        if len(roles) != len(user_to_create.roles):
            raise get_bad_request_exception(
                "Uno o mas de los roles seleccionados son invalidos."
            )

        # Create user
        created_user = self.user_service.create_user(user_to_create)
        # Assign roles to user
        if not created_user or not created_user.id:
            raise get_bad_request_exception("No se pudo crear el usuario.")

        self.user_role_service.assign_roles_to_user(
            created_user.id, user_to_create.roles
        )

        return created_user
