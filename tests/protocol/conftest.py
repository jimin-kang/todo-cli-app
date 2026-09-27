from pathlib import Path

import pytest

from di_todo_app.database.session import get_db_url, get_engine, get_session_maker
from di_todo_app.models.database import Base
from di_todo_app.protocol.database import DatabaseTodoRepository
from di_todo_app.protocol.json import JsonTodoRepository
from di_todo_app.protocol.memory import InMemoryTodoRepository


# fixture: return the protocol implementation based on the request
@pytest.fixture(
    params=["memory", "json", "database"],
    scope="function"
)
def repository(request: pytest.FixtureRequest, tmp_path: Path):
    if request.param == "memory":
        yield InMemoryTodoRepository()

    if request.param == "json":
        yield JsonTodoRepository(
            json_path = tmp_path / "todos.json"
        )

    if request.param == "database":
        db_engine = get_engine(db_url=get_db_url(db_path=tmp_path / "todos.db"))
        SessionLocal = get_session_maker(engine=db_engine)
        Base.metadata.create_all(db_engine) # create Database tables
        with SessionLocal() as session:
            yield DatabaseTodoRepository(session=session)
