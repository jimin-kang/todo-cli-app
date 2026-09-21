from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

def get_db_url(db_path: Path) -> str:
    return f"sqlite:///{db_path}"

def get_engine(db_url: str) -> Engine:
    return create_engine(db_url)

def get_session_maker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )