from typing import List
from app.core.models.base import SmartCityBqBaseModel
from sqlmodel import Session, select
from app.core.database.repositories.module_repository_impl import ModuleRepositoryImpl
from app.core.models.role import DbRole
from app.core.models.user_role import DbUserRole
from app.core.repositories.role_repository import RoleRepository


class RoleRepositoryImpl(RoleRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_roles_by_user_id(self, user_id: int) -> list[DbRole]:
        user_roles = self.session.exec(
            select(DbUserRole).where(DbUserRole.user_id == user_id)
        ).all()

        if not user_roles:
            return []

        role_ids = [user_role.role_id for user_role in user_roles]

        roles = self.session.exec(select(DbRole).where(DbRole.id.in_(role_ids))).all()  # type: ignore

        return list(roles)
