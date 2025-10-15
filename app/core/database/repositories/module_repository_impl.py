from sqlmodel import Session, select

from app.core.models.module import DbModule
from app.core.models.module_role import DbModuleRole
from app.core.repositories.module_repository import ModuleRepository


class ModuleRepositoryImpl(ModuleRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_modules_by_role_ids(self, role_ids: list[int]) -> list[DbModule]:
        if not role_ids:
            return []

        modules_roles_statement = select(DbModuleRole).where(
            DbModuleRole.role_id.in_(role_ids)  # type: ignore
        )

        modules_roles = self.session.exec(modules_roles_statement)
        print(modules_roles)
        modules_ids = [mr.module_id for mr in modules_roles]

        statement = (
            select(DbModule)
            .where(DbModule.id.in_(modules_ids))  # type: ignore
            .distinct()
        )

        results = self.session.exec(statement).all()
        return list(results)

    def get_modules_by_ids(self, module_ids: list[int]) -> list[DbModule]:
        if not module_ids:
            return []

        statement = select(DbModule).where(DbModule.id.in_(module_ids))  # type: ignore
        results = self.session.exec(statement).all()
        return list(results)

    def get_all_modules(self) -> list[DbModule]:
        statement = select(DbModule)
        results = self.session.exec(statement).all()
        return list(results)

    def get_module_by_id(self, module_id: int) -> DbModule | None:
        statement = select(DbModule).where(DbModule.id == module_id)
        return self.session.exec(statement).first()
