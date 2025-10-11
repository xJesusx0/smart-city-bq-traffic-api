from sqlmodel import Field
from app.core.models.base import SmartCityBqBaseModel


class ModuleRoleBase(SmartCityBqBaseModel):
    role_id: int = Field(foreign_key="roles.id")
    module_id: int = Field(foreign_key="modules.id")


class DbModuleRole(ModuleRoleBase, table=True):
    __tablename__ = "modules_roles"
