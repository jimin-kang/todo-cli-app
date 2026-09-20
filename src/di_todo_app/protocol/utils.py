    
from datetime import datetime
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from di_todo_app.exception.exception import DuplicateListFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoListDatabase
from di_todo_app.models.database import ToDoListDB

"""
Utility functions for our protocol implementations.
"""

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