import json
from typing import List
from rich.console import Console
from rich.table import Table

from di_todo_app.models.core import ToDo, ToDoList

def display_todo_item(todo_item: ToDo) -> Table:
    """
    Return a table of the ToDo item content.
    """
    table = Table(title=f"ToDo: {todo_item.name}")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created At")
    table.add_column("Due Date")
    table.add_column("Status")
        
    table.add_row(
        str(todo_item.id),
        todo_item.name,
        todo_item.description,
        str(todo_item.created_at),
        str(todo_item.due_date),
        todo_item.status.value
    )
    return table
        

def display_todo_list_content(todo_list: List[ToDo], list_name: str) -> Table:
    """
    Return a table of the ToDo list content.
    """
    table = Table(title=f"ToDoList: {list_name}")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created At")
    table.add_column("Due Date")
    table.add_column("Status")
        
    for todo in todo_list:
        table.add_row(
            str(todo.id),
            todo.name,
            todo.description,
            str(todo.created_at),
            str(todo.due_date),
            todo.status.value
        )
    
    return table
    
        
def display_todo_lists(todo_lists: List[ToDoList], table_title: str = "ToDoLists") -> Table:
    """
    Return a table containing metadata for all the ToDo lists.
    """

    table = Table(title=f"{table_title}")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created At")
    table.add_column("Item Count")
        
    for todo_list in todo_lists:
        table.add_row(
            str(todo_list.id),
            todo_list.name,
            todo_list.description,
            str(todo_list.created_at),
            str(todo_list.item_count)
        )
    
    return table
        
    