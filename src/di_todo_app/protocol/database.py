from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from di_todo_app.exception.exception import ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList
from di_todo_app.models.database import ToDoDB, ToDoListDB
from di_todo_app.models.utils import convert_todo_to_db
from di_todo_app.protocol.utils import verify_list_exists_db, verify_new_list_db

class SQLiteTodoRepository:
    """
    TodoRepository implementation for SQLite storage. 
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
        verify_new_list_db(todo_list=todo_list, session=self.session)
        
        # if not, add it to the table
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
        verify_list_exists_db(list_name=list_name, session=self.session)
        
        query = (
            select(ToDoListDB).where(ToDoListDB.name==list_name)
        )
        todo_list_row = self.session.scalars(query).first()
        self.session.delete(todo_list_row)
        self.session.commit()
        return list_name
        

    def drop_all_lists(self) -> None:
        self.session.query(ToDoListDB).delete()
        self.session.commit()


    def update_list(self, list_name: str, updated_list: ToDoList) -> ToDoList:
        """
        Update the specified ToDoList.
        """
        verify_list_exists_db(list_name=list_name, session=self.session)
                
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
        """
        View all ToDoLists.
        """
        query = (
            select(ToDoListDB)
        )
        todo_lists = self.session.scalars(query).all()
        return [ToDoList.model_validate(todo_list) for todo_list in todo_lists] 
        
        
    def add_item(self, todo: ToDo, list_name: str) -> ToDo: 
        """
        Add the todo to the specified list.
        """
        verify_list_exists_db(list_name=list_name, session=self.session)
        
        todo_item = convert_todo_to_db(todo=todo, list_name=list_name)
        self.session.add(todo_item)
        self.session.commit()
        return todo
        
        
    def get_item(self, id: int, list_name: str) -> ToDo | None:
        """
        Get the ToDo from the list.
        """
        # verify the list exists 
        verify_list_exists_db(list_name=list_name, session=self.session)
        
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
        """
        Get all ToDos in the specified list.
        """
        # verify the list exists 
        verify_list_exists_db(list_name=list_name, session=self.session)

        # get all ToDos from the list
        get_todos_query = (
            select(ToDoDB).where(ToDoDB.list_name==list_name)
        )
        todo_rows = self.session.scalars(get_todos_query).all()
        return [ToDo.model_validate(todo) for todo in todo_rows]
            
        
    def update_item(self, id: int, new_todo: ToDo, list_name: str) -> ToDo:
        """
        Update the item in the list.
        """
        # verify the list exists 
        verify_list_exists_db(list_name=list_name, session=self.session)
        
        todo_to_update = self.session.query(ToDoDB).filter(ToDoDB.id==id).first()
        if todo_to_update:
            # TODO: update item in some other way
            todo_to_update.name = new_todo.name
            todo_to_update.description = new_todo.description
            todo_to_update.due_date = new_todo.due_date
            todo_to_update.status = new_todo.status
            
            self.session.commit()
            
            return new_todo
        else:
            raise ItemNotFound(f"ToDo item '{id}' not found, cannot update.")
        
    
    def delete_item(self, id: int, list_name: str) -> None:
        """
        Delete the ToDo from the database.
        """
        # verify the list exists 
        verify_list_exists_db(list_name=list_name, session=self.session)
                
        # verify the item exists
        todo_to_delete = self.session.query(ToDoDB).filter(ToDoDB.id==id).first()
        if todo_to_delete:
            self.session.delete(todo_to_delete)
            self.session.commit()
        else:
            raise ItemNotFound(f"ToDo item '{id}' not found, cannot delete.")
    
    
    def delete_all_items(self, list_name: str) -> None:
        verify_list_exists_db(list_name=list_name, session=self.session)
        
        # Delete all ToDo items for the list
        # Must load items into memory & delete via ORM to trigger relationship cascades
        get_todos_query = (
            select(ToDoDB).where(ToDoDB.list_name==list_name)
        )
        items_to_delete = self.session.scalars(get_todos_query).all()
        for todo_item in items_to_delete:
            self.session.delete(todo_item)
        
        self.session.commit()