from typing import List

from di_todo_app.exception.exception import ItemNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoListDatabase
from di_todo_app.protocol.utils import find_item_in_list, verify_list_exists, verify_new_list


class InMemoryTodoRepository:
    """
    TodoRepository implementation for in-memory storage.
    Data will be in a single dict, where each key is a ToDoList.
    """
    def __init__(self):
        self.TODO_DB = ToDoListDatabase() # map list name: ToDoList
        
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        # add the ToDoList to the repo
        """
        If list exists, do nothing
        Otherwise, create it & add it to the datastore
        """
        verify_new_list(list_name=todo_list.name, db=self.TODO_DB)
        self.TODO_DB.items[todo_list.name] = todo_list
        return self.TODO_DB.items[todo_list.name]
        
    def drop_list(self, list_name: str) -> str:
        # drop the specified ToDoList
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        self.TODO_DB.items.pop(list_name)
        return list_name
    
    def drop_all_lists(self) -> None:
        self.TODO_DB = ToDoListDatabase()
    
    def update_list(self, list_name: str, updated_list: ToDoList) -> ToDoList:
        """
        Update the specified ToDoList.
        """
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        
        # delete the data keyed at the original list name if the list name has changed
        if list_name != updated_list.name:
            self.TODO_DB.items.pop(list_name)
        self.TODO_DB.items |= {updated_list.name: updated_list}
        
        return updated_list
    
        
    def view_all_lists(self) -> List[ToDoList]:
        # view all ToDoLists
        """
        Fetch all ToDoList entries from the datastore
        """
        return list(self.TODO_DB.items.values())

    def get_list(self, list_name: str) -> ToDoList | None:
        return self.TODO_DB.items.get(list_name, None)
                
        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        # add the ToDo to the specified list
        """
        If the list doesn't exist, do nothing/raise exception
        Otherwise, add the item to the ToDoList
        """
        verify_list_exists(list_name=list_name, db=self.TODO_DB)

        self.TODO_DB.items[list_name].items.append(todo)
        return todo
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        # get the ToDo from the list
        """
        If the list doesn't exist, do nothing/raise exception
        Otherwise, get the item from the list
        """
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        
        item, _ = find_item_in_list(item_id=id, todo_list=self.TODO_DB.items[list_name])
        return item
    
    
    def view_list(self, list_name: str) -> List[ToDo]: 
        # get all ToDos in the specified list
        """
        If the list doesn't exist, do nothing/raise exception
        Otherwise, get all items from the list
        """
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        return self.TODO_DB.items[list_name].items
    
    def update_item(self, id: int, new_todo: ToDo, list_name: str) -> ToDo:
        # update the item in the list
        """
        If the list doesn't exist, do nothing/raise exception
        If the item doesn't exist, do nothing/raise exception
        Otherwise, overwrite specified the item
        """
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        
        todo_list = self.TODO_DB.items[list_name]
        item, index = find_item_in_list(item_id=id, todo_list=todo_list)
        if item is None:
            raise ItemNotFound(f"ToDo item '{id}' not found, cannot update.")
        todo_list.items[index] = new_todo
        return new_todo                
    
    def delete_item(self, id: int, list_name: str) -> None:
        # delete the ToDo by ID in the list
        """
        If the list doesn't exist, do nothing/raise exception
        If the item doesn't exist, do nothing/raise exception
        Otherwise, remove the item
        """
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        
        todo_list = self.TODO_DB.items[list_name]
        item, index = find_item_in_list(item_id=id, todo_list=todo_list)
        if item is None:
            raise ItemNotFound(f"Failed to delete non-existent ToDo item '{id}'")
        todo_list.items.pop(index)
    
    def delete_all_items(self, list_name: str) -> None:
        verify_list_exists(list_name=list_name, db=self.TODO_DB)
        self.TODO_DB.items[list_name].items.clear()