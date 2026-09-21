from collections.abc import Generator, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from di_todo_app.cli.cli import TodoShell
from di_todo_app.config.config import AppConfig, load_config
from di_todo_app.database.session import get_db_url, get_engine, get_session_maker
from di_todo_app.exception.exception import InvalidConfiguration
from di_todo_app.models.core import ToDo, ToDoList
from di_todo_app.models.database import Base
from di_todo_app.protocol.core import TodoRepository
from di_todo_app.protocol.database import DatabaseTodoRepository
from di_todo_app.protocol.json import JsonTodoRepository
from di_todo_app.protocol.memory import InMemoryTodoRepository
from di_todo_app.service.service import TodoService


@contextmanager
def create_repository(config: AppConfig) -> Generator[TodoRepository]:
    match config.storage_type:
        case 'memory':
            yield InMemoryTodoRepository()
        case 'json':
            yield JsonTodoRepository(json_path=config.json_path)
        case 'db':
            db_engine = get_engine(db_url=get_db_url(db_path=config.db_path))
            SessionLocal = get_session_maker(engine=db_engine)
            Base.metadata.create_all(db_engine) # create Database tables
            with SessionLocal() as session:
                yield DatabaseTodoRepository(session=session)
        case _:
            raise InvalidConfiguration(f"Unsupported storage type: {config.storage_type}.")
    
    
def main():
    """
    Application entrypoint: choose the storage service and start the application shell.
    """
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    CONFIG_PATH = PROJECT_ROOT / "config.toml"    
    
    try:
        config = load_config(config_path=CONFIG_PATH)
        with create_repository(config) as repository:
            todo_service = TodoService(repo=repository)
            TodoShell(todo_service=todo_service).cmdloop()
            
    except InvalidConfiguration as e:
        print(f"Invalid app configuration: {e}.\nFix your configuration and re-run the application.")
    

if __name__ == '__main__':
    main()




        
