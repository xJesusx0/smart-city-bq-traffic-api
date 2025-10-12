from app.core.models.user import UserBase
from app.core.models.module import ModuleBase


class UserWithModulesDTO(UserBase):
    """
    Data Transfer Object for a user, including the list of modules they have access to.
    """
    modules: list[ModuleBase]