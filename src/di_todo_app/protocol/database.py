from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from di_todo_app.exception.exception import DuplicateListFound, ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList
from di_todo_app.models.database import ToDoDB, ToDoListDB
from di_todo_app.models.utils import convert_todo_to_db
from di_todo_app.protocol.utils import find_item_in_list

class DatabaseTodoRepository:
    """
    TodoRepository implementation for Database storage. 
    """
    
    def __init__(self, session: Session):
        """
        Establish the database session.
        """
        self.session = session
        
        # set the next available IDs for ToDo and ToDoList records
        self._set_class_ids()
        
        
    def _set_class_ids(self) -> None:
        """
        Set the class counters to the next available ID.
        """
        # Set the ToDo ID
        todo_id_stmt = select(func.max(ToDoDB.id))
        todo_max_id = self.session.scalar(todo_id_stmt)
        if todo_max_id:
            ToDo.set_counter(counter_val = todo_max_id)
        
        # Set the ToDoList ID
        todo_list_id_stmt = select(func.max(ToDoListDB.id))
        todo_list_max_id = self.session.scalar(todo_list_id_stmt)
        if todo_list_max_id:
            ToDoList.set_counter(counter_val = todo_list_max_id)        
        
        
    def create_list(self, todo_list: ToDoList) -> ToDoList:
        """
        Add the todo_list to the database if it doesn't exist
        """
        self.verify_new_list(list_name=todo_list.name)
        
        todo_list_row = ToDoListDB(
            name=todo_list.name,
            description=todo_list.description,
            created_at=todo_list.created_at
        )
        self.session.add(todo_list_row)
        self.session.commit()
        return todo_list
    
    
    def get_list(self, list_name: str) -> ToDoList | None:
        query = (
            select(ToDoListDB).where(ToDoListDB.name==list_name)
        )
        todo_list_row = self.session.scalars(query).first()
        return ToDoList.model_validate(todo_list_row) if todo_list_row else None   
        
            
    def drop_list(self, list_name: str) -> str:
        """
        Drop the specified list from the database.
        """
        list_to_drop = self.verify_list_exists(list_name=list_name)
        
        query = (
            select(ToDoListDB).where(ToDoListDB.name==list_name)
        )
        todo_list_row = self.session.scalars(query).first()
        self.session.delete(todo_list_row)
        self.session.commit()
        return list_name
        

    def drop_all_lists(self) -> None:
        # Delete all ToDoLists 
        # Must load them into memory & delete via ORM to trigger relationship cascades
        get_todo_lists_query = (
            select(ToDoListDB)
        )
        lists_to_delete = self.session.scalars(get_todo_lists_query).all()
        for todo_list in lists_to_delete:
            self.session.delete(todo_list)
            
        self.session.commit()


    def update_list(self, list_name: str, updated_list: ToDoList) -> ToDoList:
        self.verify_list_exists(list_name=list_name)
                
        query = (
            select(ToDoListDB).where(ToDoListDB.name==list_name)
        )
        todo_list_row = self.session.scalars(query).first()
        
        if todo_list_row:
            todo_list_row.name = updated_list.name
            todo_list_row.description = updated_list.description
            
            self.session.commit()
            
            return updated_list
        else:
            # This shouldn't happen since we verify the list exists before executing the query.
            # Adding this to satisfy the return signature.
            raise ListNotFound(f"ToDoList '{list_name}' not found.")
                
        
    def view_all_lists(self) -> List[ToDoList]:
        query = (
            select(ToDoListDB)
        )
        todo_lists = self.session.scalars(query).all()
        return [ToDoList.model_validate(todo_list) for todo_list in todo_lists] 
        
        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        self.verify_list_exists(list_name=list_name)
        
        todo_item = convert_todo_to_db(todo=todo, list_name=list_name)
        self.session.add(todo_item)
        self.session.commit()
        return todo
        
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        self.verify_list_exists(list_name=list_name)
        
        # Fetch the item from the list
        get_item_query = (
            select(ToDoDB).where(
                ToDoDB.list_name==list_name,
                ToDoDB.id==id
            )
        )
        todo_item = self.session.scalars(get_item_query).first()
        return ToDo.model_validate(todo_item) if todo_item else None            
        
    
    def view_list(self, list_name: str) -> List[ToDo]: 
        self.verify_list_exists(list_name=list_name)

        get_todos_query = (
            select(ToDoDB).where(ToDoDB.list_name==list_name)
        )
        todo_rows = self.session.scalars(get_todos_query).all()
        return [ToDo.model_validate(todo) for todo in todo_rows]
            
        
    def update_item(self, id: int, new_todo: ToDo, list_name: str) -> ToDo:
        todo_list = self.verify_list_exists(list_name=list_name)
        item, index = self.verify_item_exists(todo_list=todo_list, item_id=id)
        
        todo_to_update = self.session.query(ToDoDB).filter(ToDoDB.id==id).first()
        if todo_to_update:
            todo_to_update.name = new_todo.name
            todo_to_update.description = new_todo.description
            todo_to_update.due_date = new_todo.due_date
            todo_to_update.status = new_todo.status
            
            self.session.commit()
            return new_todo
        else:
            raise ItemNotFound(f"ToDo item '{id}' not found, cannot update.")
        
    
    def delete_item(self, id: int, list_name: str) -> None:
        todo_list = self.verify_list_exists(list_name=list_name)
        item, index = self.verify_item_exists(todo_list=todo_list, item_id=id)
        
        todo_to_delete = self.session.query(ToDoDB).filter(ToDoDB.id==id, ToDoDB.list_name==list_name).first()
        if todo_to_delete:
            self.session.delete(todo_to_delete)
            self.session.commit()
        else:
            # this should never happen since we verify list and item existence
            raise ItemNotFound(f"ToDo item '{id}' not found, cannot delete.")
    
    
    def delete_all_items(self, list_name: str) -> None:
        self.verify_list_exists(list_name=list_name)
        
        # Delete all ToDo items for the list
        # Must load items into memory & delete via ORM to trigger relationship cascades
        get_todos_query = (
            select(ToDoDB).where(ToDoDB.list_name==list_name)
        )
        items_to_delete = self.session.scalars(get_todos_query).all()
        for todo_item in items_to_delete:
            self.session.delete(todo_item)
        
        self.session.commit()
    
    
    def verify_list_exists(self, list_name: str) -> ToDoList:
        """
        Return the ToDoList if it exists, otherwise raise an error.
        """
        list_exists_query = (
            select(ToDoListDB).where(ToDoListDB.name==list_name)
        )
        todo_list = self.session.scalars(list_exists_query).first()
        if not todo_list:
            raise ListNotFound(f"ToDoList '{list_name}' not found.")
        return ToDoList.model_validate(todo_list)
    
    
    def verify_new_list(self, list_name: str) -> None:
        """
        Raise an error if a ToDoList exists with the same name.
        """
        list_exists_query = (
            select(ToDoListDB).where(ToDoListDB.name==list_name)
        )
        todo_list_row = self.session.scalars(list_exists_query).first()
        if todo_list_row:
            raise DuplicateListFound(f"ToDoList '{list_name}' already exists.")
    
        
    def verify_item_exists(self, todo_list: ToDoList, item_id: int) -> tuple[ToDo, int]:
        """
        Verify the ToDo item exists in the ToDoList.
        """
        item, index = find_item_in_list(item_id=item_id, todo_list=todo_list)
        if not item:
            raise ItemNotFound(f"ToDo item ID '{item_id}' not found in ToDoList '{todo_list.name}'.")
        return item, index