import json
import os
from pathlib import Path
from typing import List

from di_todo_app.exception.exception import DuplicateListFound, ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoListDatabase
from di_todo_app.protocol.utils import custom_json_serializer, find_item_in_list

# Path to data
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = ROOT_DIR / "data" 

class FileSystemTodoRepository:
    """
    TodoRepository implementation for JSON file storage.
    """
    
    def __init__(self):
        """
        Initialize the JSON database.
        """
        self.JSON_DB: Path = Path(DATA_DIR) / "db.json"
        
        # Create the file if it doesn't exist
        if not os.path.exists(self.JSON_DB):
            self._write_db(db=ToDoListDatabase())
            
        # Set the next IDs for ToDo and ToDoList records.
        # Need to do this since we assign IDs in memory.
        self._set_class_ids()
        
        
    def _load_db(self) -> ToDoListDatabase:
        """
        Load the JSON file into an in-memory database.
        """
        with open(self.JSON_DB, 'r') as f:
            return ToDoListDatabase.model_validate_json(f.read())
        
        
    def _write_db(self, db: ToDoListDatabase) -> None:
        """
        Write the in-memory database to JSON.
        """
        with open(self.JSON_DB, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, default=custom_json_serializer)
    
    
    def _set_class_ids(self) -> None:
        """
        Set the IDs for ToDo and ToDoList records.
        """
        db = self._load_db().items
        
        todo_list_max_id = 0
        todo_max_id = 0
        for _, todo_list in db.items():
            todo_list_max_id = max(todo_list_max_id, todo_list.id)
            for todo_item in todo_list.items:
                todo_max_id = max(todo_max_id, todo_item.id)
        
        ToDoList.set_counter(counter_val = todo_list_max_id)
        ToDo.set_counter(counter_val = todo_max_id)    
        
            
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        self.verify_new_list(list_name=todo_list.name)
        
        db = self._load_db()
        db.items[todo_list.name] = todo_list
        self._write_db(db)        
        
        return db.items[todo_list.name]


    def get_list(self, list_name: str) -> ToDoList | None:
        db = self._load_db()
        return db.items.get(list_name, None)

    
    def drop_list(self, list_name: str) -> str:
        self.verify_list_exists(list_name=list_name)
        
        db = self._load_db()
        db.items.pop(list_name)
        self._write_db(db)
        
        return list_name
    
    
    def drop_all_lists(self) -> None:
        self._write_db(db=ToDoListDatabase())
    
    def update_list(self, list_name: str, updated_list: ToDoList) -> ToDoList:
        self.verify_list_exists(list_name=list_name)
        
        db = self._load_db()
        
        # pop the original ToDoList if the list name has changed,
        # then add the updated list content
        if list_name != updated_list.name:
            db.items.pop(list_name) 
        db.items |= {updated_list.name: updated_list}
        
        self._write_db(db)
        return updated_list
                
        
    def view_all_lists(self) -> List[ToDoList]:
        return list(self._load_db().items.values())
        
        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        self.verify_list_exists(list_name=list_name)
        
        db = self._load_db()
        db.items[list_name].items.append(todo)
        self._write_db(db)
        
        return todo
        
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        todo_list = self.verify_list_exists(list_name=list_name)
        item, _ = find_item_in_list(item_id=id, todo_list=todo_list)
        return item   
        
    
    def view_list(self, list_name: str) -> List[ToDo]: 
        todo_list = self.verify_list_exists(list_name=list_name)
        return todo_list.items
        
        
    def update_item(self, id: int, new_todo: ToDo, list_name: str) -> ToDo:
        todo_list = self.verify_list_exists(list_name=list_name)
        _, index = self.verify_item_exists(todo_list=todo_list, item_id=id)
        
        # update the ToDoList with the updated item
        todo_list.items[index] = new_todo
        
        # write it to the database
        db = self._load_db()
        db.items |= {todo_list.name: todo_list}
        self._write_db(db)
        
        return new_todo
        
    
    def delete_item(self, id: int, list_name: str) -> None:
        todo_list = self.verify_list_exists(list_name=list_name)
        _, index = self.verify_item_exists(todo_list=todo_list, item_id=id)
                
        # delete the ToDo from the ToDoList by index
        db = self._load_db()
        todo_list.items.pop(index)
        db.items |= {todo_list.name: todo_list}
        self._write_db(db)


    def delete_all_items(self, list_name: str) -> None:
        todo_list = self.verify_list_exists(list_name=list_name)
        
        db = self._load_db()
        todo_list.items.clear()
        db.items |= {todo_list.name: todo_list}        
        self._write_db(db)
        
        
    def verify_list_exists(self, list_name: str) -> ToDoList:
        db = self._load_db()
        if list_name not in db.items:
            raise ListNotFound(f"ToDoList '{list_name}' not found.")
        return db.items[list_name]
    
    
    def verify_new_list(self, list_name: str) -> None:
        db = self._load_db()
        if list_name in db.items:
            raise DuplicateListFound(f"ToDoList '{list_name}' already exists.")       
    
        
    def verify_item_exists(self, todo_list: ToDoList, item_id: int) -> tuple[ToDo, int]:
        item, index = find_item_in_list(item_id=item_id, todo_list=todo_list)
        if not item:
            raise ItemNotFound(f"ToDo item ID '{item_id}' not found in ToDoList '{todo_list.name}'.")
        return item, index
        