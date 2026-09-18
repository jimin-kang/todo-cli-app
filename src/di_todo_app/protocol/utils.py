    
from datetime import datetime
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from di_todo_app.exception.exception import DuplicateListFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoListDatabase
from di_todo_app.models.database import ToDoListDB


def verify_list_exists(list_name: str, db: ToDoListDatabase):
    """
    Check if the list exists.

    Args:
        list_name (str): List to find

    Raises:
        ListNotFound: raised if the list is not found
    """
    if list_name not in db.items:
        raise ListNotFound(f"ToDoList '{list_name}' not found.")

def verify_list_exists_db(list_name: str, session: Session):
    """
    Verify the ToDoList exists in the database (ToDoListDB).
    """
    list_exists_query = (
        select(ToDoListDB).where(ToDoListDB.name==list_name)
    )
    todo_list = session.scalars(list_exists_query).first()
    if not todo_list:
        raise ListNotFound(f"ToDoList '{list_name}' not found.")


def verify_new_list(list_name: str, db: ToDoListDatabase):
    """
    Verifies the list specified by list_name does not already exist.
    Otherwise, raises an exception indicating the list already exists. 

    Args:
        list_name (str): _description_

    Raises:
        DuplicateListFound: if the list already exists
    """
    if list_name in db.items:
        raise DuplicateListFound(f"ToDoList '{list_name}' already exists.")
    
def verify_new_list_db(todo_list: ToDoList, session: Session):
    """
    Verifies the list specified by list_name does not already exist in the database (ToDoListDB).
    Otherwise, raises an exception indicating the list already exists. 

    Args:
        list_name (str): _description_

    Raises:
        DuplicateListFound: if the list already exists
    """
    list_exists_query = (
        select(ToDoListDB).where(ToDoListDB.name==todo_list.name)
    )
    todo_list_row = session.scalars(list_exists_query).first()
    if todo_list_row:
        raise DuplicateListFound(f"ToDoList '{todo_list.name}' already exists.")

def find_item_in_list(item_id: int, todo_list: ToDoList) -> tuple[ToDo, int] | tuple[None, int]:
    """
    Find the ToDo in the list of ToDos by ID.
    
    Args:
        item_id (str): _description_
        todo_list (list[ToDo]): _description_

    Returns:
        tuple[ToDo, int] | tuple[None, None]: _description_
    """
    for index, item in enumerate(todo_list.items):
        if item.id == item_id:
            return item, index
    return None, -1

def custom_json_serializer(obj: Any):
    """
    JSON serializer to handle custom objects and other non-JSON serializable types.
    """
    # Handle custom objects
    if isinstance(obj, ToDo) or isinstance(obj, ToDoList) or isinstance(obj, ToDoListDatabase):
        return obj.model_dump(mode='json')

    # Handle datetime objects
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    # Handle sets (convert to lists)
    if isinstance(obj, set):
        return list(obj)

    # Fallback to string representation if all else fails
    return str(obj)