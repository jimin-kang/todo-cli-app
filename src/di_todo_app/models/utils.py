from di_todo_app.models.core import ToDo, ToDoList
from di_todo_app.models.database import ToDoDB, ToDoListDB


def convert_todo_to_db(todo: ToDo, list_name: str) -> ToDoDB:
    """
    Translate the ToDo application model to the ToDoDB database model.
    """
    return ToDoDB(
        id=todo.id,
        name=todo.name,
        description=todo.description,
        created_at=todo.created_at,
        due_date=todo.due_date,
        status=todo.status,
        list_name=list_name
    )
    

def convert_todo_list_to_db(todo_list: ToDoList) -> ToDoListDB:
    """
    Translate the ToDo application model to the ToDoDB database model.
    """
    return ToDoListDB(
        name=todo_list.name,
        description=todo_list.description,
        created_at=todo_list.created_at,
     )