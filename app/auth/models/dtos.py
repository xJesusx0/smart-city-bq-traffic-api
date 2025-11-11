from pydantic import BaseModel

from app.core.models.module import ModuleBase
from app.core.models.role import RoleBase
from app.core.models.user import UserBase


class UserWithModulesDTO(UserBase):
    """
    Data Transfer Object for a user, including the list of modules they have access to.
    """

    modules: list[ModuleBase]
    roles: list[RoleBase]


class ChangePasswordDTO(BaseModel):
    token: str
    password: str
