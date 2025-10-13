from app.core.exceptions import (
    get_bad_request_exception,
    get_entity_not_found_exception,
)
from app.core.models.user import UserBase, UserUpdate
from app.iam.services.role_service import RoleService
from app.iam.services.user_role_service import UserRoleService
from app.iam.services.user_service import UserService


class UpdateUserUseCase:
    def __init__(
        self,
        user_service: UserService,
        role_service: RoleService,
        user_role_service: UserRoleService,
    ):
        self.user_service = user_service
        self.role_service = role_service
        self.user_role_service = user_role_service

    def invoke(self, user_id: int, user_to_update: UserUpdate) -> UserBase:
        # Validate user exists
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise get_entity_not_found_exception(
                f"Usuario con id {user_id} no encontrado"
            )

        # Validate roles if provided
        if user_to_update.roles is not None:
            roles = self.role_service.get_roles_by_ids(user_to_update.roles)
            if len(roles) != len(user_to_update.roles):
                raise get_bad_request_exception(
                    "Uno o mas de los roles seleccionados son invalidos."
                )

        # Update user
        updated_user = self.user_service.update_user(user_id, user_to_update)
        if not updated_user:
            raise get_entity_not_found_exception(
                f"No se pudo actualizar el usuario con id {user_id}"
            )

        # Sync roles
        if user_to_update.roles is not None:
            self.user_role_service.remove_all_roles_from_user(user_id)
            if user_to_update.roles:
                self.user_role_service.assign_roles_to_user(
                    user_id, user_to_update.roles
                )

        # Return user with updated data
        return self.user_service.get_user_by_id(user_id)
