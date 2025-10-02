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

        statement = (
            select(DbModule)
            .join(DbModuleRole)
            .where(DbModuleRole.role_id.in_(role_ids))  # role_ids es una lista de ints
            .distinct()
        )

        results = self.session.exec(statement).all()
        return list(results)
