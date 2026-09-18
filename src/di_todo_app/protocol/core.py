from typing import List, Protocol

from di_todo_app.models.core import ToDo, ToDoList

class TodoRepository(Protocol):
    """
    Protocol for ToDoRepository: define methods to CRUD ToDos
    """
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        # add the ToDoList to the repo
        """
        If list exists, do nothing
        Otherwise, create it & add it to the datastore
        """
        ...
    
    def drop_list(self, list_name: str) -> str:
        """
        Delete the specified ToDoList.
        """
        ...
    
    def drop_all_lists(self) -> None:
        """
        Drop all ToDoLists.
        """
    
    def get_list(self, list_name: str) -> ToDoList | None:
        """
        Get the specified ToDoList.
        """
        ...
    
    def update_list(self, list_name: str, updated_list: ToDoList) -> ToDoList:
        """
        Update the specified ToDoList.
        """
        ...
            
        
    def view_all_lists(self) -> List[ToDoList]:
        """
        View all ToDoLists: fetch all ToDoLists from the datastore.
        """
        ...
        
    def view_list(self, list_name: str) -> List[ToDo]: 
        # view all ToDos in the specified list
        """
        If the list doesn't exist, raise exception
        Otherwise, get all items from the list
        """
        ...
        
        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        # add the ToDo to the specified list
        """
        If the list doesn't exist, do nothing/raise exception
        Otherwise, add the item to the ToDoList
        """
        ...
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        # get the ToDo from the list
        """
        If the list doesn't exist, raise exception
        Otherwise, get the item from the list. If item doesn't exist, do nothing/return None.
        """
        ...
        
    def update_item(self, id: int, new_todo: ToDo, list_name: str) -> ToDo:
        # update the item in the list
        """
        If the list doesn't exist, do nothing/raise exception
        If the item doesn't exist, do nothing/raise exception
        Otherwise, overwrite specified the item
        """
        ...
    
    def delete_item(self, id: int, list_name: str) -> None:
        # delete the ToDo by ID in the list
        """
        If the list doesn't exist, do nothing/raise exception
        If the item doesn't exist, do nothing/raise exception
        Otherwise, remove the item
        """
        ...
    
    def delete_all_items(self, list_name: str) -> None:
        """
        Delete all items from the ToDoList.
        """