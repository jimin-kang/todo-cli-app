class ListNotFound(Exception):
    """Exception raised when a ToDoList is not found.."""
    pass

class DuplicateListFound(Exception):
    """Exception raised when a ToDoList already exists."""
    pass

class ItemNotFound(Exception):
    """Exception raised when a ToDo item is not found."""
    pass

class InvalidConfiguration(Exception):
    """Exception raised due to invalid app configuraiton."""
    pass