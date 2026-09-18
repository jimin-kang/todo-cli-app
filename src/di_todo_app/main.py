from collections.abc import Generator, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Literal

from di_todo_app.cli.cli import TodoShell
from di_todo_app.config.config import AppConfig, load_config
from di_todo_app.database.session import SessionLocal, engine
from di_todo_app.exception.exception import InvalidConfiguration
from di_todo_app.models.core import ToDo, ToDoList
from di_todo_app.models.database import Base
from di_todo_app.protocol.core import TodoRepository
from di_todo_app.protocol.database import SQLiteTodoRepository
from di_todo_app.protocol.file import FileSystemTodoRepository
from di_todo_app.protocol.memory import InMemoryTodoRepository
from di_todo_app.service.service import TodoService


@contextmanager
def create_repository(config: AppConfig) -> Generator[TodoRepository]:
    match config.storage_type:
        case 'json':
            yield FileSystemTodoRepository()
        case 'memory':
            yield InMemoryTodoRepository()
        case 'db':
            Base.metadata.create_all(engine) # create Database tables
            with SessionLocal() as session:
                yield SQLiteTodoRepository(session=session)
        case _:
            raise InvalidConfiguration(f"Unsupported storage type: {config.storage_type}.")
    
    
def main():
    """
    Application entrypoint: choose the storage service and start the application shell.
    """    
    try:
        config = load_config()
        with create_repository(config) as repository:
            todo_service = TodoService(repo=repository)
            TodoShell(todo_service=todo_service).cmdloop()
            
    except InvalidConfiguration as e:
        print(f"Invalid app configuration: {e}.\nFix your configuration and re-run the application.")
    

if __name__ == '__main__':
    main()




        
