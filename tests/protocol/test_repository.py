        

import pytest

from di_todo_app.exception.exception import DuplicateListFound, ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoStatus, UpdateToDoListRequest, UpdateToDoRequest
from di_todo_app.protocol.core import TodoRepository


def test_create_and_get_list(repository: TodoRepository):
    """
    Test creating a new ToDoList and fetching it.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    res = repository.get_list(list_name="groceries")
    assert res and res.id == todo_list.id and res.name == todo_list.name
    
    
def test_create_duplicate_list(repository: TodoRepository):
    """
    Test creating a ToDoList that already exists.
    Should throw a DuplicateListError.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    res = repository.get_list(list_name="groceries")
    assert res and res.id == todo_list.id and res.name == todo_list.name
    
    with pytest.raises(DuplicateListFound):
        repository.create_list(todo_list=ToDoList(name="groceries"))
        
    
def test_get_non_existent_list(repository: TodoRepository):
    """
    Test fetching a non-existent ToDoList.
    """
    assert repository.get_list(list_name="groceries") is None
        
    
def test_update_list(repository: TodoRepository):
    """
    Test updating a ToDoList.
    Subsequent fetch should contain the updated data.
    """
    original_list = ToDoList(name="groceries")
    repository.create_list(todo_list=original_list)
    
    updated_list_req = UpdateToDoListRequest(name=original_list.name, description="trader joe's stuff")
    _ = repository.update_list(list_name=original_list.name, updated_list_req=updated_list_req)
    res = repository.get_list(list_name=original_list.name)    
    
    assert res and res.id == original_list.id and res.name == updated_list_req.name and res.description == updated_list_req.description
    
    
def test_update_non_existent_list(repository: TodoRepository):
    """
    Test updating a non-existent list.
    This should raise a ListNotFound error.
    """
    with pytest.raises(ListNotFound):
        repository.update_list(list_name="groceries", updated_list_req=UpdateToDoListRequest(name="groceries", description="trader joe's stuff"))
        
    
def test_delete_list(repository: TodoRepository):
    """
    Test deletion of a list.
    Subsequent fetch should raise a ListNotFound error.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    repository.drop_list(list_name=todo_list.name)
    assert repository.get_list(list_name=todo_list.name) is None
        
    
def test_delete_non_existent_list(repository: TodoRepository):
    """
    Verify deleting a non-existent ToDoList raises a ListNotFound error.
    """
    with pytest.raises(ListNotFound):
        repository.drop_list(list_name="groceries")
    

def test_create_todo(repository: TodoRepository):
    """
    Test adding a new ToDo item to a ToDoList.
    Subsequent fetch should contain the item.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    
    todo_item = ToDo(name="bananas")
    repository.add_item(todo=todo_item, list_name=todo_list.name)
    res = repository.get_item(id=todo_item.id, list_name=todo_list.name)
    assert res and res.id == todo_item.id and res.name == todo_item.name
    
    
def test_create_todo_on_non_existent_list(repository: TodoRepository):
    """
    Test creating a new ToDo item on a non-existent list.
    This should raise a ListNotFound error.
    """
    todo_item = ToDo(name="bananas")
    with pytest.raises(ListNotFound):
        repository.add_item(todo=todo_item, list_name="groceries")
    
    
def test_get_non_existent_todo(repository: TodoRepository):
    """
    Test getting a non-existent ToDo item from a ToDoList.
    Should return None.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    
    assert repository.get_item(id=1, list_name=todo_list.name) is None
        
    
def test_get_todo_on_non_existent_list(repository: TodoRepository):
    """
    Test getting a ToDo on a non-existent list.
    This should raise a ListNotFound error.
    """
    with pytest.raises(ListNotFound):
        repository.get_item(id=1, list_name="groceries")
    
    
def test_update_todo(repository: TodoRepository):
    """
    Test updating a ToDo item.
    Subsequent fetch should contain the updated item.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    
    todo_item = ToDo(name="bananas")
    repository.add_item(todo=todo_item, list_name=todo_list.name)
    
    update_todo_request = UpdateToDoRequest(name="bananas", description="organic", status=ToDoStatus.COMPLETE)
    repository.update_item(
        id=todo_item.id,
        update_todo_req=update_todo_request,
        list_name=todo_list.name
    )
    
    res = repository.get_item(id=todo_item.id, list_name=todo_list.name)
    assert res and res.id == todo_item.id and res.name == update_todo_request.name and res.description == update_todo_request.description and res.status == update_todo_request.status
        
    
def test_update_todo_on_non_existent_list(repository: TodoRepository):
    """
    Test updating a ToDo item on a non-existent list.
    Should raise a ListNotFound error.
    """
    with pytest.raises(ListNotFound):
        repository.update_item(id=1, update_todo_req=UpdateToDoRequest(name="bananas"), list_name="groceries")
    
    
def test_update_non_existent_todo(repository: TodoRepository):
    """
    Test updating a non-existent ToDo item.
    Should raise an ItemNotFound error.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    
    with pytest.raises(ItemNotFound):
        repository.update_item(id=1, update_todo_req=UpdateToDoRequest(name="bananas"), list_name=todo_list.name)
       

def test_delete_todo(repository: TodoRepository):
    """
    Test deleting a ToDo item from a ToDoList.
    Subsequent fetch should return None.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    
    todo_item = ToDo(name="bananas")
    repository.add_item(todo=todo_item, list_name=todo_list.name)
    assert repository.get_item(id=todo_item.id, list_name=todo_list.name) == todo_item
    
    repository.delete_item(id=todo_item.id, list_name=todo_list.name)
    assert repository.get_item(id=todo_item.id, list_name=todo_list.name) is None
        
    
def test_delete_todo_on_non_existent_list(repository: TodoRepository):
    """
    Test deleting a ToDo item from a non-existent list.
    Should raise a ListNotFound error.
    """
    with pytest.raises(ListNotFound):
        repository.delete_item(id=1, list_name="groceries")
    
    
def test_delete_non_existent_todo(repository: TodoRepository):
    """
    Deleting a non-existent ToDo item should raise an ItemNotFound error.
    """
    todo_list = ToDoList(name="groceries")
    repository.create_list(todo_list=todo_list)
    
    todo_item = ToDo(name="bananas")
    repository.add_item(todo=todo_item, list_name=todo_list.name)
    assert repository.get_item(id=todo_item.id, list_name=todo_list.name) == todo_item
    
    with pytest.raises(ItemNotFound):
        repository.delete_item(id=-1, list_name=todo_list.name)
    
       