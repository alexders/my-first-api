from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

settings = get_settings()

connect_arg={ }

if settings.database_url.startswith("sqlite"):
    connect_arg = {"check_same_thread": False}
engine = create_engine(
    settings.database_url,
    echo=True,
    future=True,
    connect_args=connect_arg,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
