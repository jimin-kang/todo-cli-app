from datetime import datetime
from enum import Enum
import json
from typing import Any, ClassVar, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_serializer
from sqlmodel import Field, Relationship, SQLModel

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from di_todo_app.models.core import ToDoStatus


class Base(DeclarativeBase):
    pass


class ToDoDB(Base):
    """
    Database model for ToDo items.
    """
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[ToDoStatus] = mapped_column(Enum(ToDoStatus), default=ToDoStatus.TODO)
    
    # Foreign key pointing to the owning ToDoList
    list_name: Mapped[str] = mapped_column(ForeignKey("todo_lists.name"))

    # Python-side relationship back to the ToDoList
    list: Mapped["ToDoListDB"] = relationship(back_populates="items")
    
    
class ToDoListDB(Base):
    """
    Database model for ToDoLists.
    """
    __tablename__ = "todo_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    items: Mapped[list["ToDoDB"]] = relationship(back_populates="list", cascade="all, delete-orphan")
    
    @property
    def item_count(self) -> int:
        return len(self.items)
