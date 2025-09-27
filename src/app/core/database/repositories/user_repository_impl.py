from sqlmodel import Session, select

from src.app.core.repositories.user_repository import UserRepository
from src.app.core.models.user import DbUser

class UserRepositoryImpl(UserRepository):

    def __init__(self, session: Session):
        self.session = session

    def get_user_by_id(self, user_id: int):
        pass

    def get_user_by_login_name(self, login_name: str) -> DbUser | None:
        statement = select(DbUser).where(DbUser.login_name == login_name)

        result = self.session.exec(statement).first()
        return result
