from sqlmodel import Field

from app.core.models.base import SmartCityBqBaseModel


class UserRoleBase(SmartCityBqBaseModel):
    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")


class DbUserRole(UserRoleBase, table=True):
    __tablename__ = "users_roles"
