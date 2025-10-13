from datetime import datetime
from app.core.models.user import UserCreate, UserUpdate
from typing import Sequence
from typing import Optional
from sqlmodel import Session, select

from app.core.repositories.user_repository import UserRepository
from app.core.models.user import DbUser


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_all_users(self) -> list[DbUser]:
        statement = select(DbUser)

        results: Sequence[DbUser] = self.session.exec(statement).all()
        return list(results)

    def get_all_users_by_active(self, active: bool) -> list[DbUser]:
        if active is None:
            return self.get_all_users()

        statement = select(DbUser).where(DbUser.active == active)

        results: Sequence[DbUser] = self.session.exec(statement).all()
        return list(results)

    def get_user_by_id(self, user_id: int) -> Optional[DbUser]:
        statement = select(DbUser).where(DbUser.id == user_id)

        result = self.session.exec(statement).first()
        return result

    def get_user_by_email(self, email: str) -> Optional[DbUser]:
        statement = select(DbUser).where(DbUser.email == email)

        result = self.session.exec(statement).first()
        return result

    def delete_user_by_id(self, user_id: int) -> Optional[DbUser]:
        statement = select(DbUser).where(DbUser.id == user_id)

        user = self.session.exec(statement).first()
        if user:
            user.active = False
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)

        return user

    def create_user(self, user: UserCreate) -> DbUser:
        db_user = DbUser.model_validate(user)
        db_user.creation_date = datetime.now()
        db_user.active = True
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[DbUser]:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            if key == "roles":
                continue
            setattr(db_user, key, value)

        db_user.update_date = datetime.now()
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        return db_user
