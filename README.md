## Overview
Command line ToDo list application. Manage all your tasks and group related tasks together under separate ToDoLists.

## Requirements
* uv
* Python 3.12+

## Running the Application
1. Set up application configuration. Choose how your tasks should be stored by configuring `config.toml`.
   
2. Run the app.
```
uv run python -m di_todo_app.main
```

## Usage
| Command | Description | Example |
|---------|-------------|---------|
| `list show [list_name]` | Show metadata for one or all todo lists. Use `*` for all lists, otherwise specify the list name. | `list show groceries`  |
| `list create [list_name]` | Create a new todo list. | `list create groceries` |
| `list get [list_name]` | Get all todo items of a todo list. | `list get groceries` |
| `list update [list_name]` | Update a todo list. | `list update groceries` |
| `list delete [list_name]` | Delete one or all todo list(s). Specify `*` to delete all lists. | `list delete groceries` |
| `list clear [list_name]` | Clear the contents of a todo list. | `list clear groceries` |
| `todo add [list_name] [item_name]` | Add an item to a todo list. | `todo add groceries bananas` |
| `todo get [list_name] [item_id]` | Get an item from a todo list. | `todo get groceries 1` |
| `todo update [list_name] [item_id]` | Update an item from a todo list. | `todo update groceries 1` |
| `todo delete [list_name] [item_id]` | Delete an item from a todo list. | `todo add groceries bananas` |
