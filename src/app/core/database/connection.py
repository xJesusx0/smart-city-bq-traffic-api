from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.database.repositories.user_repository_impl import UserRepositoryImpl
from app.core.repositories.user_repository import UserRepository

engine = create_engine("mysql+pymysql://root:081880@localhost:3306/smart_city_bq")

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]