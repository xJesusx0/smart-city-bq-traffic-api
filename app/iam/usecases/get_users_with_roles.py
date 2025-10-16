from app.core.models.role import RoleBase
from app.iam.dtos.user_with_roles import UserWithRolesDTO
from app.iam.services.role_service import RoleService
from app.iam.services.user_service import UserService


class GetUsersWithRolesUseCase:
    def __init__(self, user_service: UserService, role_service: RoleService):
        self.user_service = user_service
        self.role_service = role_service

    def invoke(self, active: bool | None = None) -> list[UserWithRolesDTO]:
        users = self.user_service.get_all_users(active=active)
        if not users:
            return []

        user_ids = [u.id for u in users if u.id is not None]
        roles_map = self.role_service.get_roles_map_by_user_ids(user_ids)

        result: list[UserWithRolesDTO] = []
        for user in users:
            roles = roles_map.get(user.id or -1, [])
            roles = [RoleBase.model_validate(role) for role in roles]
            dto: UserWithRolesDTO = UserWithRolesDTO(roles=roles, **user.model_dump())
            result.append(dto)

        return result
