from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .dependencies import get_settings

settings = get_settings()
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """
    Get DB Session SQLAlchemy object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
