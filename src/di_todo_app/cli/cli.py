import copy
from datetime import datetime, timedelta
import json
from textwrap import dedent

import cmd2
from cmd2 import Cmd2ArgumentParser, Color, stylize, with_argparser
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

from di_todo_app.exception.exception import ItemNotFound, ListNotFound
from di_todo_app.models.core import ToDo, ToDoList, ToDoStatus
from di_todo_app.service.service import TodoService


from datetime import datetime
from rich.prompt import Confirm, InvalidResponse, Prompt, PromptBase
from rich.console import Console

from di_todo_app.cli.utils import display_todo_lists, display_todo_item, display_todo_list_content

# Global Console
console = Console()

# Constants
WILDCARD = "*"

class DatePrompt(PromptBase[datetime]):
    """
    A prompt for a datetime.
    Used to ask for a ToDo item's due date .

    Args:
        PromptBase (_type_): _description_

    Raises:
        InvalidResponse: _description_

    Returns:
        _type_: _description_
    """
    response_type = datetime
    validate_error_message = "[prompt.invalid]Please enter a valid datetime."
    
    def process_response(self, value: str) -> datetime:
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d")
        except ValueError:
            raise InvalidResponse(self.validate_error_message)        

class TodoShell(cmd2.Cmd):
    """
    USAGE:
    - list show <list name> <*>
    - list create <name>
    - list drop <name>
    - todo add <list name>
    - todo get <list name> <item ID>
    - todo update <list name> <item ID>
    - todo delete <list name> <item ID>
    """
    def __init__(self, todo_service: TodoService, *args, **kwargs):
        """
        Create the application shell. 
        Inject the TodoService and call its corresponding methods.
        """
        # Initialize cmd2 first
        super().__init__(*args, **kwargs)
        self.intro = stylize(
            "Stuff ToDo: your favorite ToDo List :)", 
            style=Style(color=Color.GREEN1, bold=True)
        ) 
        self.prompt = "todo> "
        
        # Color to output text in with echo command
        self.foreground_color = 'cyan'
        
        # Store our todo service
        self.todo_service = todo_service
    

    # LIST COMMAND PARSER
    list_parser = Cmd2ArgumentParser(
        prog="list",
        description="Manage your todo lists!",
    )
    list_subparsers = list_parser.add_subparsers(
        dest="command"
    )

    # list show <list name> <*>
    show_list_parser = list_subparsers.add_parser(
        "show",
        help="Display metadata for one/all todo lists",
    )
    show_list_parser.add_argument(
        "name",
        default="*",
        help="Name of the todo list to display. Default value is '*', which shows all todo lists.",
    )
    
    # list get <list name>
    get_list_parser = list_subparsers.add_parser(
        "get",
        help="Display the contents of a todo list",
    )
    get_list_parser.add_argument(
        "name",
        help="Name of the todo list to display",
    )
    
    # list create <list name>
    create_list_parser = list_subparsers.add_parser(
        "create",
        help="Create a todo list",
    )
    create_list_parser.add_argument(
        "name",
        help="Name of the todo list to create",
    )
    
    # list update <list name>
    update_list_parser = list_subparsers.add_parser(
        "update",
        help="Update a todo list",
    )
    update_list_parser.add_argument(
        "name",
        help="Name of the todo list to update",
    )

    # list delete <list name> <*>
    delete_list_parser = list_subparsers.add_parser(
        "delete",
        help="Delete a todo list",
    )
    delete_list_parser.add_argument(
        "name",
        help="Name of the todo list to delete. Enter '*' to delete all todo lists.",
    )
    
    # list clear <list name>
    clear_list_parser = list_subparsers.add_parser(
        "clear",
        help="Clear the contents of a todo list",
    )
    clear_list_parser.add_argument(
        "name",
        help="Name of the todo list to clear",
    )

    @with_argparser(list_parser)
    def do_list(self, args):
        """Manage todo lists."""

        match args.command:
            case "show":
                if args.name == WILDCARD:
                    # show all lists
                    all_lists = self.todo_service.view_all_lists()                
                    console.print(display_todo_lists(todo_lists=all_lists))
                else:            
                    # show the specific list
                    todo_list = self.todo_service.get_list(list_name=args.name)
                    if todo_list:
                        console.print(display_todo_lists(todo_lists=[todo_list], table_title=f"ToDoList: {todo_list.name}"))
                    else:
                        self.poutput(f"List '{args.name}' not found.")
                
            case "get": 
                try:
                    all_list_items = self.todo_service.view_list(list_name=args.name)
                    console.print(display_todo_list_content(todo_list=all_list_items, list_name=args.name))
                except ListNotFound as e:
                    console.print(f"Failed to display ToDoList '{args.name}': {e}")
                    
            case "create":
                new_todo_list = self.todo_service.create_list(todo_list=ToDoList(name=args.name))
                console.print(f"ToDoList '{new_todo_list.name}' created!")
                    
            case "update":
                try:
                    # Input form to update todo list (populated with existing values)
                    current_list = self.todo_service.get_list(list_name=args.name)
                    if current_list:
                        console.print("\n[bold yellow]--- Current ToDoList ---[/]")
                        console.print(display_todo_lists(todo_lists=[current_list], table_title=f"ToDoList: {current_list.name}"))
                        
                        # update the list
                        console.print("\n[bold yellow]--- Update ToDoList (Press Enter to keep existing value) ---[/]")
                        name = Prompt.ask(
                            "[yellow]Name[/yellow]",
                            default=current_list.name
                        )
                        description = Prompt.ask(
                            "[yellow]Description[/yellow]",
                            default=current_list.description
                        )
                        
                        updated_todo_list = copy.deepcopy(current_list)
                        updated_todo_list.name = name
                        updated_todo_list.description = description
                        
                        console.print(display_todo_lists(todo_lists=[updated_todo_list], table_title=f"ToDoList: {updated_todo_list.name}"))
                        update_list = Confirm.ask(
                            dedent(f"""[bold green]Proceed with the updated ToDoList?[/bold green]""")
                        )
                        if update_list:
                            self.todo_service.update_list(
                                list_name=args.name,
                                updated_list=updated_todo_list,
                            )
                            print(f"Successfully updated ToDoList '{args.name}'.")
                        else:
                            print(f"Cancelled update of ToDoList '{args.name}'.")
                    else:
                        raise ListNotFound(f"ToDoList '{args.name}' not found.")
                except (ListNotFound, ItemNotFound) as e:
                    console.print(f"Failed to update ToDoList '{args.name}': {e}")
            

            case "delete":
                if args.name == WILDCARD: # deleting ALL lists
                    drop_all_lists = Confirm.ask(
                        dedent(f"""[bold red]Drop all ToDo Lists? This cannot be undone.""")
                    )
                    if drop_all_lists:
                        self.todo_service.drop_all_lists()
                        self.poutput(f"Dropped all ToDoLists.")
                    else:
                        self.poutput(f"Cancelling deletion of all lists.")    
                else: # deleting a single list
                    list_to_delete = self.todo_service.get_list(list_name=args.name)
                    
                    if list_to_delete:
                        delete_list = Confirm.ask(
                            dedent(f"""
                                    [bold green]Delete list '{args.name}'? 
                                    Name: [cyan]{list_to_delete.name}[/cyan] 
                                    Description: [cyan]{list_to_delete.description}[/cyan]
                                    Item Count: [cyan]{list_to_delete.item_count}[/cyan]"""
                            )
                        )
                        if delete_list:
                            dropped_list = self.todo_service.drop_list(list_name=args.name)
                            self.poutput(f"Successfully deleted list: {dropped_list}")
                        else:
                            self.poutput(f"Cancelling deletion of list '{args.name}'.")
                    else:
                        self.poutput(f"List '{args.name}' doesn't exist, nothing to delete.")
                        
            case "clear":
                # clear the contents of the ToDoList
                try:
                    clear_list = Confirm.ask(
                        dedent(f"""[bold red]Drop all items from ToDoList '{args.name}'? This cannot be undone.""")
                    )
                    if clear_list:
                        self.todo_service.delete_all_items(list_name=args.name)
                        self.poutput(f"Dropped all items from ToDoList '{args.name}'.")
                    else:
                        self.poutput(f"Cancelling deletion of all items from ToDoList '{args.name}'.")
                except ListNotFound as e:
                    console.print(f"Failed to clear ToDoList '{args.name}': {e}")
            
            case _:
                self.poutput("Use 'list -h' for help.")

    
    # ToDo COMMAND PARSER
    todo_parser = Cmd2ArgumentParser(
        prog="list",
        description="Manage your todo items! Create, read, update, or delete them from their corresponding list.",
    )
    todo_subparsers = todo_parser.add_subparsers(
        dest="command"
    )

    # todo add <list name> <todo name>
    add_todo_parser = todo_subparsers.add_parser(
        "add",
        help="Add a todo to a list.",
    )
    add_todo_parser.add_argument(
        "list_name",
        help="Name of the todo list to add to.",
    )
    add_todo_parser.add_argument(
        "item_name",
        help="Name of the todo item to add.",
    )
    
    # todo get <list name> <todo ID>
    get_todo_parser = todo_subparsers.add_parser(
        "get",
        help="Get a todo from a list.",
    )
    get_todo_parser.add_argument(
        "list_name",
        help="Name of the todo list to get the todo from.",
    )
    get_todo_parser.add_argument(
        "item_id",
        type=int,
        help="ID of the todo item to get.",
    )
    
    # todo update <list name> <todo ID>
    update_todo_parser = todo_subparsers.add_parser(
        "update",
        help="Update a todo within a list.",
    )
    update_todo_parser.add_argument(
        "list_name",
        help="Name of the todo list to update the todo from.",
    )
    update_todo_parser.add_argument(
        "item_id",
        type=int,
        help="ID of the todo item to update.",
    )
    
    # todo delete <list name> <todo ID>
    delete_todo_parser = todo_subparsers.add_parser(
        "delete",
        help="Delete a todo from a list.",
    )
    delete_todo_parser.add_argument(
        "list_name",
        help="Name of the todo list to delete the todo from.",
    )
    delete_todo_parser.add_argument(
        "item_id",
        type=int,
        help="ID of the todo item to delete.",
    )
    @with_argparser(todo_parser)
    def do_todo(self, args):
        """Manage todo items."""

        match args.command:
            case "add":
                # Create new ToDo item from Rich prompts
                console.print(Panel(f"[bold cyan]Add a new ToDo item to list '{args.list_name}'![/bold cyan]", border_style="blue"))
                
                name = Prompt.ask(
                    "[yellow]Name[/yellow]",
                    default=args.item_name
                )
                description = Prompt.ask("[yellow]Description[/yellow]")
                due_date = DatePrompt.ask(
                    "[yellow]Due date[/yellow]", 
                    default=(datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
                )
                status = Prompt.ask(
                    "[yellow]Status[/yellow]", 
                    choices=[ToDoStatus.TODO.value, ToDoStatus.PENDING.value, ToDoStatus.COMPLETE.value], 
                    default=ToDoStatus.TODO.value
                )
                
                # Confirm whether to add the new ToDo item
                add_item = Confirm.ask(
                    dedent(f"""
                           [bold green]Add the following ToDo item to list '{args.list_name}'? 
                             Name: [cyan]{name}[/cyan] 
                             Description: [cyan]{description}[/cyan]
                             Due Date: [cyan]{due_date}[/cyan]
                             Status: [cyan]{status}[/cyan][/bold green]""")
                    )
                if add_item:
                    try:
                        self.todo_service.add_item(
                            todo=ToDo(
                                name=args.item_name,
                                description=description,
                                due_date=due_date,
                                status=ToDoStatus(status)
                            ),
                            list_name=args.list_name
                        )
                        console.print(f"Added item '{args.item_name}' to list '{args.list_name}'")
                    except ListNotFound as e:
                        print(f"Failed to add ToDo item '{args.item_name}' to list '{args.list_name}': {e}")
                else:
                    console.print("Canceling add item request.")
                    
                                        
            case "get":
                try:
                    todo_item = self.todo_service.get_item(id=args.item_id, list_name=args.list_name)
                    if todo_item:
                        console.print(display_todo_item(todo_item=todo_item))
                    else:
                        console.print(f"ToDo item with ID '{args.item_id}' not found in list '{args.list_name}'")
                except ListNotFound as e:
                    console.print(f"Failed to fetch ToDo item with ID '{args.item_id}' from list '{args.list_name}': {e}")
        

            case "update":
                try:
                    # Input form to update todo item (populated with existing values)
                    current_item = self.todo_service.get_item(id=args.item_id, list_name=args.list_name)
                    if current_item:
                        console.print("\n[bold yellow]--- Current ToDo Item ---[/]")
                        console.print(display_todo_item(todo_item=current_item))
                        
                        # update the item
                        console.print("\n[bold yellow]--- Update ToDo Item (Press Enter to keep existing value) ---[/]")
                        name = Prompt.ask(
                            "[yellow]Name[/yellow]",
                            default=current_item.name
                        )
                        description = Prompt.ask(
                            "[yellow]Description[/yellow]",
                            default=current_item.description
                        )
                        due_date = DatePrompt.ask(
                            "[yellow]Due date[/yellow]", 
                            default=current_item.due_date
                        )
                        status = Prompt.ask(
                            "[yellow]Status[/yellow]", 
                            choices=[ToDoStatus.TODO.value, ToDoStatus.PENDING.value, ToDoStatus.COMPLETE.value], 
                            default=current_item.status
                        )
                        
                        updated_item = copy.deepcopy(current_item)
                        updated_item.name = name
                        updated_item.description = description
                        updated_item.due_date = due_date
                        updated_item.status = ToDoStatus(status)
                        
                        console.print(display_todo_item(todo_item=updated_item))
                        update_item = Confirm.ask(
                            dedent(f"""[bold green]Proceed with the updated ToDo item?[/bold green]""")
                        )
                        if update_item:
                            self.todo_service.update_item(
                                id=args.item_id,
                                todo=updated_item,
                                list_name=args.list_name
                            )
                            print(f"Successfully updated item '{args.item_id}' from list '{args.list_name}'.")
                        else:
                            print(f"Cancelled update of item '{args.item_id}' from list '{args.list_name}'.")
                    else:
                        raise ItemNotFound(f"ToDo item with ID '{args.item_id}' not found in list '{args.list_name}'.")
                except (ListNotFound, ItemNotFound) as e:
                    console.print(f"Failed to update ToDo item with ID '{args.item_id}' in list '{args.list_name}': {e}")
            
            case "delete":
                try:
                    item_to_delete = self.todo_service.get_item(id=args.item_id, list_name=args.list_name)
                    if item_to_delete:
                        # confirm deletion
                        console.print(display_todo_item(item_to_delete))
                        delete_item = Confirm.ask(
                            dedent(f"""[bold green]Delete the above ToDo item from list '{args.list_name}'?[/bold green]""")
                        )
                        if delete_item:
                            self.todo_service.delete_item(id=args.item_id, list_name=args.list_name)
                            print(f"Successfully deleted item '{args.item_id}' from list '{args.list_name}'.")
                        else:
                            print(f"Cancelled deletion of item '{args.item_id}' from list '{args.list_name}'.")
                    else:
                        raise ItemNotFound(f"Item of ID '{args.item_id}' not found in list '{args.list_name}'")
                except (ListNotFound, ItemNotFound) as e:
                    print(f"Failed to delete ToDo item '{args.item_id}' from list '{args.list_name}': {e}")
                    
            case _:
                self.poutput("Use 'todo -h' for help.")
    
    # End terminal upon 'exit' or 'quit'
    def do_exit(self, args):
        """
        Exit the application.
        """
        print("Closing the ToDo application.")
        return True
    

    