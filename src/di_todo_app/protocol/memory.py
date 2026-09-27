import copy
from typing import List

from di_todo_app.exception.exception import DuplicateListFound, ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoListDatabase, UpdateToDoListRequest, UpdateToDoRequest
from di_todo_app.protocol.utils import find_item_in_list


class InMemoryTodoRepository:
    """
    TodoRepository implementation for in-memory storage.
    Data will be in a single dict, where each key is a ToDoList.
    """
    def __init__(self):
        self.TODO_DB = ToDoListDatabase() # map list name: ToDoList
        
        
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        self.verify_new_list(list_name=todo_list.name)
        self.TODO_DB.items[todo_list.name] = todo_list
        return self.TODO_DB.items[todo_list.name]
        
        
    def drop_list(self, list_name: str) -> str:
        list_to_drop = self.verify_list_exists(list_name=list_name)
        self.TODO_DB.items.pop(list_to_drop.name)
        return list_to_drop.name
    
    
    def drop_all_lists(self) -> None:
        self.TODO_DB = ToDoListDatabase()
    
    
    def update_list(self, list_name: str, updated_list_req: UpdateToDoListRequest) -> ToDoList:
        _ = self.verify_list_exists(list_name=list_name)
        
        # delete original list
        current_list = self.TODO_DB.items.pop(list_name)
        
        # create the updated list & add it
        updated_list = copy.deepcopy(current_list)
        updated_list.name = updated_list_req.name
        updated_list.description = updated_list_req.description
        self.TODO_DB.items |= {updated_list.name: updated_list}
        
        return updated_list
    
        
    def view_all_lists(self) -> List[ToDoList]:
        return list(self.TODO_DB.items.values())


    def get_list(self, list_name: str) -> ToDoList | None:
        return self.TODO_DB.items.get(list_name, None)        

        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        _ = self.verify_list_exists(list_name=list_name)
        self.TODO_DB.items[list_name].items.append(todo)
        return todo

        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        _ = self.verify_list_exists(list_name=list_name)
        item, _ = find_item_in_list(item_id=id, todo_list=self.TODO_DB.items[list_name])
        return item
    
    
    def view_list(self, list_name: str) -> List[ToDo]: 
        todo_list = self.verify_list_exists(list_name=list_name)
        return todo_list.items
    
    
    def update_item(self, id: int, update_todo_req: UpdateToDoRequest, list_name: str) -> ToDo:
        todo_list = self.verify_list_exists(list_name=list_name)
        curr_item, index = self.verify_item_exists(todo_list=todo_list, item_id=id)
        
        # create the updated item from the request, add it to the ToDoList
        updated_item = copy.deepcopy(curr_item)
        updated_item.name = update_todo_req.name
        updated_item.description = update_todo_req.description
        updated_item.due_date = update_todo_req.due_date
        updated_item.status = update_todo_req.status
        todo_list.items[index] = updated_item
        
        return updated_item         
           
    
    def delete_item(self, id: int, list_name: str) -> None:
        todo_list = self.verify_list_exists(list_name=list_name)
        _, index = self.verify_item_exists(todo_list=todo_list, item_id=id)        
        todo_list.items.pop(index)
    
    
    def delete_all_items(self, list_name: str) -> None:
        list_to_clear = self.verify_list_exists(list_name=list_name)
        self.TODO_DB.items[list_to_clear.name].items.clear()
        
        
    def verify_list_exists(self, list_name: str) -> ToDoList:
        if list_name not in self.TODO_DB.items:
            raise ListNotFound(f"ToDoList '{list_name}' not found.")
        return self.TODO_DB.items[list_name]
        
        
    def verify_new_list(self, list_name: str) -> None:
        if list_name in self.TODO_DB.items:
            raise DuplicateListFound(f"ToDoList '{list_name}' already exists.")
    
    
    def verify_item_exists(self, todo_list: ToDoList, item_id: int) -> tuple[ToDo, int]:
        item, index = find_item_in_list(item_id=item_id, todo_list=todo_list)
        if not item:
            raise ItemNotFound(f"ToDo item ID '{item_id}' not found in ToDoList '{todo_list.name}'.")
        return item, index
        
        