from typing import List, Protocol

from di_todo_app.models.core import ToDo, ToDoList, UpdateToDoListRequest, UpdateToDoRequest

class TodoRepository(Protocol):
    """
    ToDoRepository defines a contract for retrieving and persisting ToDoLists and ToDo items.\n
    """
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        """
        Create a new ToDoList.
        
        Raises an exception if a list with the same name already exists.
        """
        ...
    
    def drop_list(self, list_name: str) -> str:
        """
        Delete the specified ToDoList.
        
        Raises an exception if the list isn't found.
        """
        ...
    
    def drop_all_lists(self) -> None:
        """
        Drop all ToDoLists.
        """
    
    def get_list(self, list_name: str) -> ToDoList | None:
        """
        Return the specified ToDoList if it exists.
        Otherwise, return None.
        """
        ...
    
    def update_list(self, list_name: str, updated_list_req: UpdateToDoListRequest) -> ToDoList:
        """
        Update the specified ToDoList.
        
        Raises an exception if the list isn't found.
        """
        ...
        
    def view_all_lists(self) -> List[ToDoList]:
        """
        Fetch all ToDoLists.
        """
        ...
        
    def view_list(self, list_name: str) -> List[ToDo]: 
        """
        Fetch all ToDo items in the specified ToDoList.
        
        Raises an exception if the list isn't found.
        """
        ...
        
        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        """
        Add a ToDo item to the specified ToDoList.
        
        Raises an exception if the list isn't found.
        """
        ...
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        """
        Get the ToDo item from the specified ToDoList.
        If it doesn't exist, return None.
        
        Raises an exception if the list isn't found.
        """
        ...
        
    def update_item(self, id: int, update_todo_req: UpdateToDoRequest, list_name: str) -> ToDo:
        """
        Update the ToDo item in the specified ToDoList.
        
        Raises an exception if the list isn't found or if the item isn't found.
        """
        ...
    
    def delete_item(self, id: int, list_name: str) -> None:
        """
        Delete a ToDo item from the specified ToDoList.
        
        Raises an exception if the list isn't found or if the item isn't found. 
        """
        ...
    
    def delete_all_items(self, list_name: str) -> None:
        """
        Delete all items from the specified ToDoList.
        
        Raises an exception if the list isn't found.
        """
        ...
    
    def verify_list_exists(self, list_name: str) -> ToDoList:
        """
        Verify the specified ToDoList exists.
        
        Return the ToDoList if found. Otherwise, raise an exception.
        """
        ...
    
    def verify_new_list(self, list_name: str) -> None:
        """
        Verify the specified ToDoList doesn't exist.
        
        Raises an exception if a ToDoList exists with the same name.
        """
        ...
        
    def verify_item_exists(self, todo_list: ToDoList, item_id: int) -> tuple[ToDo, int]:
        """
        Verify the ToDo item exists in the specified ToDoList.
        
        Return the ToDo item with its corresponding index in the list if found. Otherwise, raise an exception.
        """
        ...