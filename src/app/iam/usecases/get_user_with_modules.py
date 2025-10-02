from app.iam.services.user_service import UserService
from app.core.exceptions import get_entity_not_found_exception
from app.iam.dtos.user import UserWithModulesDTO
from app.iam.services.module_service import ModuleService
from app.core.repositories.user_repository import UserRepository
from app.core.models.module import ModuleBase


class GetUserWithModulesUseCase:
    """
    Use case to retrieve a user's details along with all the modules they have access to
    through their assigned roles.
    """

    def __init__(self, user_service: UserService, module_service: ModuleService):
        self.user_service = user_service
        self.module_service = module_service

    def invoke(self, user_id: int) -> UserWithModulesDTO:
        """
        Executes the use case.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A DTO containing the user's information and their accessible modules.

        Raises:
            HTTPException: If the user with the given ID is not found.
        """
        # 1. Get user with their associated roles
        user_with_roles = self.user_service.get_user_with_roles_by_id(user_id)
        if not user_with_roles:
            raise get_entity_not_found_exception(
                f"Usuario con id {user_id} no encontrado"
            )

        # 2. Extract role IDs from the user's roles
        role_ids = [role.id for role in user_with_roles.roles if role.id is not None]

        # 3. Get all unique modules for the collected role IDs
        modules = []
        if role_ids:
            db_modules = self.module_service.get_modules_by_role_ids(role_ids)
            # Convert DbModule objects to ModuleBase for the DTO
            modules = [ModuleBase.model_validate(m) for m in db_modules]

        # 4. Construct and return the DTO
        user_dto = UserWithModulesDTO(
            **user_with_roles.model_dump(
                exclude={"roles"}
            ),  # Exclude roles from the final DTO
            modules=modules,
        )

        return user_dto
