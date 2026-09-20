import json
from typing import List

from di_todo_app.exception.exception import DuplicateListFound, ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList
from di_todo_app.protocol.core import TodoRepository


class TodoService:
    """
    TodoService translates user input into application logic.\n
    User commands will trigger calls to the appropriate repository method.
    """
    def __init__(self, repo: TodoRepository):
        self.repo = repo
    
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        """
        Create the new ToDoList.
        """
        return self.repo.create_list(todo_list=todo_list)
    
    def drop_list(self, list_name: str) -> str:
        """
        Drop the specified ToDoList.

        Args:
            list_name (str): _description_
        """
        return self.repo.drop_list(list_name)

    def drop_all_lists(self) -> None:
        """
        Delete all ToDoLists from the repo.
        """
        return self.repo.drop_all_lists()
    
    def get_list(self, list_name: str) -> ToDoList | None:
        """
        Get the specified ToDoList.

        Args:
            list_name (str): _description_

        Returns:
            ToDoList | None: _description_
        """
        return self.repo.get_list(list_name=list_name)
    
    def update_list(self, list_name: str, updated_list: ToDoList) -> ToDoList:
        """
        Update the specified ToDoList.
        """
        return self.repo.update_list(list_name=list_name, updated_list=updated_list)
        
    def view_all_lists(self) -> List[ToDoList]:
        """
        Return all ToDoLists to display.
        """
        return self.repo.view_all_lists()
        
    
    def view_list(self, list_name: str) -> List[ToDo]:
        """
        Return all the items of the ToDoList.
        """
        return self.repo.view_list(list_name=list_name)
        
        
    def add_item(self, todo: ToDo, list_name: str) -> None: 
        """
        Add the ToDo item to the specified ToDoList.

        Args:
            todo (ToDo): _description_
            list_name (str): _description_
        """
        self.repo.add_item(todo=todo, list_name=list_name)
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        """
        Get the ToDo item from the specified ToDoList.

        Args:
            id (str): _description_
            list_name (str): _description_

        Returns:
            ToDo | None: _description_
        """
        return self.repo.get_item(id=id, list_name=list_name)
                    
        
    def update_item(self, id: int, todo: ToDo, list_name: str) -> ToDo:
        """
        Update the specified ToDo item in the ToDoList.

        Args:
            id (str): _description_
            todo (ToDo): _description_
            list_name (str): _description_
        """
        return self.repo.update_item(id=id, new_todo=todo, list_name=list_name)
                    
        
    def delete_item(self, id: int, list_name: str) -> None:
        """
        Delete the specified ToDo item from the ToDoList.

        Args:
            id (str): _description_
            list_name (str): _description_
        """
        self.repo.delete_item(id=id, list_name=list_name)    


    def delete_all_items(self, list_name: str) -> None:
        """
        Delete all items from the specified ToDoList.

        Args:
            list_name (str): ToDoList to clear
        """
        self.repo.delete_all_items(list_name=list_name)