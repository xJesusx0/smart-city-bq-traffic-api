from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.settings import settings

engine = create_engine(settings.db_url)


def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]
