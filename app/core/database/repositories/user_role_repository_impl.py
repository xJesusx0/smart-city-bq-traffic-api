from sqlmodel import Session, select

from app.core.models.user_role import DbUserRole
from app.core.repositories.user_role_repository import UserRoleRepository


class UserRoleRepositoryImpl(UserRoleRepository):
    def __init__(self, session: Session):
        self.session = session

    def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        user_role = DbUserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        self.session.commit()

    def remove_role_from_user(self, user_id: int, role_id: int) -> None:
        user_role = self.session.exec(
            select(DbUserRole).where(
                DbUserRole.user_id == user_id, DbUserRole.role_id == role_id
            )
        ).one()

        if user_role:
            user_role.active = False
            self.session.add(user_role)
            self.session.commit()

    def assign_roles_to_user(self, user_id: int, role_ids: list[int]) -> None:
        # Trae todos los user_roles existentes (activos o no)
        user_roles = self.session.exec(
            select(DbUserRole).where(
                DbUserRole.user_id == user_id,
                DbUserRole.role_id.in_(role_ids),  # type: ignore
            )
        ).all()

        # IDs de roles ya existentes
        existing_role_ids = [ur.role_id for ur in user_roles]

        # Reactiva los roles inactivos
        for ur in user_roles:
            if not ur.active:
                ur.active = True

        # Crea los nuevos roles que no existan aún
        new_user_roles = [
            DbUserRole(user_id=user_id, role_id=role_id)
            for role_id in role_ids
            if role_id not in existing_role_ids
        ]

        # Guarda todo
        self.session.add_all(new_user_roles)
        self.session.commit()

    def remove_all_roles_from_user(self, user_id: int) -> None:
        user_roles = self.session.exec(
            select(DbUserRole).where(DbUserRole.user_id == user_id)
        ).all()

        for user_role in user_roles:
            user_role.active = False
            self.session.add(user_role)

        self.session.commit()
