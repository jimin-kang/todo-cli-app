from datetime import datetime
from enum import Enum
import json
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_serializer
from sqlmodel import Field, Relationship, SQLModel

class ToDoStatus(Enum):
    """
    Different statuses of a ToDo item
    """
    TODO = "todo"
    PENDING = "pending"
    COMPLETE = "complete"

class ToDo(BaseModel):
    """
    Definition of a ToDo item
    """
    # ClassVar tells Pydantic not to treat this as a model field
    _counter: ClassVar[int] = 0 # NOTE: this must be set appropriately upon app startup if data is persisted to file/DB to avoid duplicate IDs
    
    id: int = Field(default_factory=lambda: ToDo.get_next_id())
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    status: ToDoStatus = ToDoStatus.TODO
    
    # enable loading the database model into the pydantic model from the attribute names
    model_config = ConfigDict(from_attributes=True) 
    
    @classmethod
    def get_next_id(cls) -> int:
        cls._counter += 1
        return cls._counter
    
    @classmethod
    def set_counter(cls, counter_val: int):
        """
        Set the class counter value.
        
        Call this to set the counter upon app startup to the next available ID that has yet to be persisted.
        """
        cls._counter = counter_val
    

class ToDoList(BaseModel):
    """
    ToDoList definition: a list of related ToDo items
    """
    _counter: ClassVar[int] = 0 # NOTE: this must be set appropriately upon app startup if data is persisted to file/DB to avoid duplicate IDs

    id: int = Field(default_factory=lambda: ToDoList.get_next_id()) # TODO: DELETE THIS, LOAD ID FROM DATABASE (DOESN'T PERSIST BETWEEN RUNS)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    items: List[ToDo] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def get_next_id(cls) -> int:
        cls._counter += 1
        return cls._counter
    
    @classmethod
    def set_counter(cls, counter_val: int):
        """
        Set the class counter value.
        
        Call this to set the counter upon app startup to the next available ID that has yet to be persisted.
        """
        cls._counter = counter_val
    
    @computed_field
    @property
    def item_count(self) -> int:
        return len(self.items)
    
    def to_display(self, tabular: bool = True) -> Dict[str, Any]:
        """
        Returns a dict containing the ToDoList contents.
        By default, omits the `items` so we can display ToDoList in tabular format (i.e. display item count only instead of the individual ToDo item content).
        """
        data = self.model_dump(mode="json")

        if tabular:
            data.pop("items")

        return data
    

class ToDoListDatabase(BaseModel):
    items: dict[str, ToDoList] = {} # map {list name : ToDoList}
    model_config = ConfigDict(from_attributes=True)

