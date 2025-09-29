from app.core.settings import settings
from typing import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session

engine = create_engine(settings.db_url)


def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]
