from app.core.models.role import RoleBase
from app.core.models.user import UserBase


class UserWithRolesDTO(UserBase):
    roles: list[RoleBase]
