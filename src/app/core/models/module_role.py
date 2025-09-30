from sqlmodel import Field, Relationship
from app.core.models.base import SmartCityBqBaseModel
from app.core.models.module import DbModule
from app.core.models.role import DbRole


class ModuleRoleBase(SmartCityBqBaseModel):
    role_id: int = Field(foreign_key="roles.id")
    module_id: int = Field(foreign_key="modules.id")


class DbModuleRole(ModuleRoleBase, table=True):
    __tablename__ = "modules_roles"


class ModuleWithRoles(DbModule):
    roles: list[DbRole] = Relationship(
        back_populates="modules", link_model=DbModuleRole
    )


class RoleWithModules(DbRole):
    modules: list[DbModule] = Relationship(
        back_populates="roles", link_model=DbModuleRole
    )
