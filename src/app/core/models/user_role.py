from sqlmodel import Field, Relationship
from app.core.models.base import SmartCityBqBaseModel
from app.core.models.user import DbUser
from app.core.models.role import DbRole


class UserRoleBase(SmartCityBqBaseModel):
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")


class DbUserRole(UserRoleBase, table=True):
    __tablename__ = "users_roles"


class UserWithRoles(DbUser):
    roles: list["DbRole"] = Relationship(back_populates="users", link_model=DbUserRole)


class RoleWithUsers(DbRole):
    users: list["DbUser"] = Relationship(back_populates="roles", link_model=DbUserRole)
