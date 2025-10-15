from datetime import datetime
from typing import Optional, Sequence

from sqlmodel import Session, select

from app.core.models.role import DbRole, RoleCreate, RoleUpdate
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

    def get_all_roles(self) -> list[DbRole]:
        statement = select(DbRole)
        results: Sequence[DbRole] = self.session.exec(statement).all()
        return list(results)

    def get_all_roles_by_active(self, active: bool) -> list[DbRole]:
        statement = select(DbRole).where(DbRole.active == active)
        results: Sequence[DbRole] = self.session.exec(statement).all()
        return list(results)

    def get_role_by_id(self, role_id: int) -> Optional[DbRole]:
        statement = select(DbRole).where(DbRole.id == role_id)
        result = self.session.exec(statement).first()
        return result

    def create_role(self, role: RoleCreate) -> DbRole:
        db_role = DbRole.model_validate(role)
        db_role.creation_date = datetime.now()
        db_role.active = True
        self.session.add(db_role)
        self.session.commit()
        self.session.refresh(db_role)
        return db_role

    def update_role(self, role_id: int, role: RoleUpdate) -> Optional[DbRole]:
        db_role = self.get_role_by_id(role_id)
        if not db_role:
            return None

        role_data = role.model_dump(exclude_unset=True)
        for key, value in role_data.items():
            if key == "modules":
                continue

            setattr(db_role, key, value)

        db_role.update_date = datetime.now()
        self.session.add(db_role)
        self.session.commit()
        self.session.refresh(db_role)

        return db_role

    def delete_role_by_id(self, role_id: int) -> Optional[DbRole]:
        statement = select(DbRole).where(DbRole.id == role_id)
        role = self.session.exec(statement).first()
        if role:
            role.active = False
            self.session.add(role)
            self.session.commit()
            self.session.refresh(role)

        return role

    def get_roles_by_ids(self, role_ids: list[int]) -> list[DbRole]:
        if not role_ids:
            return []

        roles = self.session.exec(select(DbRole).where(DbRole.id.in_(role_ids))).all()  # type: ignore
        return list(roles)

    def get_roles_by_user_ids_map(self, user_ids: list[int]) -> dict[int, list[DbRole]]:
        if not user_ids:
            return {}

        # Fetch all user-role relations for the provided user IDs
        user_roles = self.session.exec(
            select(DbUserRole).where(DbUserRole.user_id.in_(user_ids))  # type: ignore
        ).all()

        if not user_roles:
            return {}

        # Collect distinct role IDs
        role_ids = list({ur.role_id for ur in user_roles})
        if not role_ids:
            return {}

        # Fetch all roles in a single query
        roles = self.session.exec(select(DbRole).where(DbRole.id.in_(role_ids))).all()  # type: ignore
        roles_by_id: dict[int, DbRole] = {
            role.id: role for role in roles if role.id is not None
        }

        # Build mapping from user_id to roles
        result: dict[int, list[DbRole]] = {}
        for ur in user_roles:
            # Skip relations whose role is missing (defensive)
            role = roles_by_id.get(ur.role_id)
            if role is None:
                continue
            bucket = result.setdefault(ur.user_id, [])
            bucket.append(role)

        return result
