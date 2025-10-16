from app.core.models.module import ModuleBase
from app.core.models.role import RoleBase


class RoleWithModulesDTO(RoleBase):
    modules: list[ModuleBase]
