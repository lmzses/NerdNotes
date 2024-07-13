import argparse
import os
import re
import shlex
import subprocess
import textwrap
import time
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from dateutil import parser
from prompt_toolkit import prompt
from prompt_toolkit.keys import Keys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

NERDNOTES_DIR = Path.home() / ".nerdnotes"
NOTES_DIR = NERDNOTES_DIR / "notes"
TODOS_DIR = NERDNOTES_DIR / "todos"

notes = []
todos = []
selected_row = 0


# Clear screen function
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# Display logo
def display_logo():
    logo = """
    _   _              _ _   _       _
   | \\ | |            | | \\ | |     | |
   |  \\| | ___ _ __ __| |  \\| | ___ | |_ ___  ___
   | . ` |/ _ \\ '__/ _` | . ` |/ _ \\| __/ _ \\/ __|
   | |\\  |  __/ | | (_| | |\\  | (_) | ||  __/\\__ \\
   |_| \\_|\\___|_|  \\__,_|_| \\_|\\___/ \\__\\___||___/

    """
    console.print(Panel(logo, style="bold blue", expand=False))


def display_options():
    options = (
        "[bold cyan]Use ↑/↓ to navigate,[/bold cyan] "
        "[bold white]Enter to select,[/bold white] "
        "[bold red]r to delete,[/bold red] "
        "[bold yellow]e to edit,[/bold yellow] "
        "[bold white]q to quit.[/bold white]"
    )
    console.print(options)


def display_todo_options():
    options = (
        "[bold cyan]Use ↑/↓ to navigate,[/bold cyan] "
        "[bold white]Enter to view todo details,[/bold white] "
        "[bold red]r to delete,[/bold red] "
        "[bold yellow]e to edit,[/bold yellow] "
        "[bold blue]x to mark as complete/incomplete, [/bold blue]"
        "[bold white]q to quit.[/bold white]"
    )
    console.print(options)


def refresh_notes():
    global notes
    notes = []
    for file in NOTES_DIR.glob("*.md"):
        with file.open("r") as f:
            content = f.read()
            metadata = yaml.safe_load(content.split("---")[1])
            created_str = (
                metadata["created"].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(metadata["created"], datetime)
                else str(metadata["created"])
            )
            notes.append((file.stem, metadata["title"], created_str))


def refresh_todos():
    global todos
    todos = []
    todos_file = TODOS_DIR / "todos.txt"
    if todos_file.exists():
        with todos_file.open("r") as f:
            todos = [line.strip().split("|") for line in f.readlines()]


def create_key_bindings():
    from prompt_toolkit.key_binding import KeyBindings

    kb = KeyBindings()

    @kb.add(Keys.Up)
    def _(event):
        event.app.exit(result="up")

    @kb.add(Keys.Down)
    def _(event):
        event.app.exit(result="down")

    @kb.add(Keys.Enter)
    def _(event):
        event.app.exit(result="enter")

    @kb.add("e")
    def _(event):
        event.app.exit(result="e")

    @kb.add("r")
    def _(event):
        event.app.exit(result="r")

    @kb.add("x")
    def _(event):
        event.app.exit(result="x")

    @kb.add("q")
    def _(event):
        event.app.exit(result="q")

    return kb


# Wrap text for display
def wrap_text(text, width):
    return "\n".join(textwrap.wrap(text, width))


# Sanitize title for filename
def sanitize_filename(title):
    sanitized = re.sub(r"[^\w\-_]", "", title.replace(" ", "_"))
    return sanitized if sanitized else "untitled"


# Extract due date from todo description
def extract_due_date(description):
    description = description.lower()
    if "tomorrow" in description:
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    elif "today" in description:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        due_date = parser.parse(description, fuzzy=True)
        return due_date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


# Create todo
def create_todo(todo_id, description, due_date=None):
    todos_file = TODOS_DIR / "todos.txt"
    TODOS_DIR.mkdir(parents=True, exist_ok=True)

    with todos_file.open("a") as f:
        f.write(
            f"{todo_id}|{description}|incomplete|{time.strftime('%Y-%m-%d %H:%M:%S')}|{due_date or ''}\n"
        )

    print(f"Todo created: {todo_id}")


# Add todo
def add_todo(todo_description):
    todo_id = f"todo_{int(time.time())}"
    due_date = extract_due_date(todo_description)
    create_todo(todo_id, todo_description, due_date)


def get_todos_table():
    table = Table(title="Your Todos", show_header=True, header_style="bold blue")
    table.add_column("Description", style="magenta", width=30)
    table.add_column("Status", style="green", width=10)
    table.add_column("Due Date", style="yellow", width=25)
    table.add_column("Created", style="dim", width=20)

    for i, (todo_id, description, status, created, due_date) in enumerate(todos):
        row_style = "reverse" if i == selected_row else ""
        status_marker = "[X]" if status == "complete" else "[ ]"
        table.add_row(
            wrap_text(description, 50),
            status_marker,
            due_date,
            created,
            style=row_style,
        )
    return table


def edit_todo(todo_id):
    todos_file = TODOS_DIR / "todos.txt"
    if not todos_file.exists():
        console.print(f"Todo file not found.", style="bold red")
        return

    todos_list = []
    todo_found = False

    with todos_file.open("r") as f:
        for line in f:
            parts = line.strip().split("|")
            if parts[0] == todo_id:
                todo_found = True
                console.print(f"Current Description: {parts[1]}")
                new_description = prompt(
                    "Enter new description (leave empty to keep current): "
                ).strip()
                if new_description:
                    parts[1] = new_description

                console.print(f"Current Status: {parts[2]}")
                new_status = prompt(
                    "Enter new status (leave empty to keep current): "
                ).strip()
                if new_status:
                    parts[2] = new_status

                new_due_date = extract_due_date(parts[1])
                if new_due_date:
                    parts[4] = new_due_date

            todos_list.append("|".join(parts))

    if not todo_found:
        console.print(f"Todo '{todo_id}' not found.", style="bold red")
        return

    with todos_file.open("w") as f:
        for todo in todos_list:
            f.write(f"{todo}\n")

    refresh_todos()
    console.print(f"Todo '{todo_id}' updated.", style="bold green")


# List todos
def list_todos():
    global selected_row
    selected_row = 0
    todos_file = TODOS_DIR / "todos.txt"
    if not todos_file.exists():
        console.print("No todos found.", style="bold red")
        return

    with todos_file.open("r") as f:
        for line in f:
            todo_id, description, status, created, due_date = line.strip().split("|")
            todos.append((todo_id, description, status, created, due_date))
    while True:
        clear_screen()
        console.print(get_todos_table())
        display_todo_options()
        key = prompt("", key_bindings=create_key_bindings())

        if key == "q":
            break
        elif key == "x":
            selected_todo = todos[selected_row][0]
            complete_todo(selected_todo)

        elif key == "e":
            selected_todo = todos[selected_row][0]
            edit_todo(selected_todo)
            styled_input = Panel(
                Text(
                    "Press Enter to return to the todos list.",
                    style="bold green on black",
                ),
                border_style="bright_blue",
                expand=False,
            )
            console.print(styled_input)
            input()
        elif key == "r":
            selected_todo = todos[selected_row][0]
            # Confirmation prompt_toolkit
            confirm = prompt(
                f"Are you sure you want to delete the todo {selected_todo}'? (y/n): "
            )
            if confirm.lower() == "y":
                delete_todo(selected_todo)
                console.print(
                    f"Todo '{selected_todo}' has been deleted.", style="bold green"
                )
            else:
                console.print("Deletion cancelled.", style="bold yellow")

            styled_input = Panel(
                Text(
                    "Press Enter to return to the todos list.",
                    style="bold green on black",
                ),
                border_style="bright_blue",
                expand=False,
            )
            console.print(styled_input)
            input()
        elif key == "up":
            selected_row = max(0, selected_row - 1)
        elif key == "down":
            selected_row = min(len(todos) - 1, selected_row + 1)
        elif key == "enter":
            selected_todo = todos[selected_row][0]
            view_todo_detail(selected_todo)
            styled_input = Panel(
                Text(
                    "Press Enter to return to the todos list",
                    style="bold green on black",
                ),
                border_style="bright_blue",
                expand=False,
            )
            console.print(styled_input)
            input()


def view_todo_detail(todo_id):
    todos_file = TODOS_DIR / "todos.txt"
    if not todos_file.exists():
        console.print(f"Todo '{todo_id}' not found.", style="bold red")
        return

    with todos_file.open("r") as f:
        for line in f:
            tid, description, status, created, due_date = line.strip().split("|")
            if tid == todo_id:
                console.print(f"[bold]ID:[/bold] {tid}")
                console.print(f"[bold]Description:[/bold] {description}")
                console.print(f"[bold]Status:[/bold] {status}")
                console.print(f"[bold]Created:[/bold] {created}")
                console.print(f"[bold]Due Date:[/bold] {due_date}")
                return
    console.print(f"Todo '{todo_id}' not found.", style="bold red")


# Complete todo
def complete_todo(todo_id):
    todos_file = TODOS_DIR / "todos.txt"
    if not todos_file.exists():
        print("No todos found.")
        return

    with todos_file.open("r") as f:
        todos = f.readlines()
    updated = False
    for i, todo in enumerate(todos):
        if todo.startswith(todo_id):
            if "|incomplete|" in todos[i]:
                todos[i] = todo.replace("|incomplete|", "|complete|", 1)
                updated = True
                break
            else:
                todos[i] = todo.replace("|complete|", "|incomplete|", 1)
                updated = True
                break
    if updated:
        with todos_file.open("w") as f:
            f.writelines(todos)
        refresh_todos()


def delete_todo(todo_id):
    todos_file = TODOS_DIR / "todos.txt"
    if not todos_file.exists():
        console.print("No todos found.", style="Bold red")
        return

    with todos_file.open("r") as f:
        todos = f.readlines()

    updated_todos = [todo for todo in todos if not todo.startswith(todo_id)]

    if len(updated_todos) != len(todos):
        with todos_file.open("w") as f:
            f.writelines(updated_todos)
        print(f"Todo '{todo_id}' deleted.")
        refresh_todos()
    else:
        print(f"Todo '{todo_id}' not found.")


# Note Management Functions
def create_note(title, content=""):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_title = sanitize_filename(title)
    filename = f"{timestamp}_{safe_title}.md"
    filepath = NOTES_DIR / filename

    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    with filepath.open("w") as f:
        f.write("---\n")
        f.write(f"title: {title}\n")
        f.write(f"created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("tags: \n")
        f.write("---\n\n")
        f.write(f"# {title}\n\n")
        f.write(content)

    print(f"Note created: {filepath}")


def find_note(note_id):
    for file in NOTES_DIR.glob("*.md"):
        if note_id.lower() in file.stem.lower():
            return file
    return None


def edit_note(note_id):
    note_file = find_note(note_id)
    if not note_file:
        console.print(f"Note '{note_id}' not found.", style="bold red")
        return

    # Open the note in the default text editor
    try:
        subprocess.run(["nano", str(note_file)])  # Use your preferred editor
        # Optionally for Windows, you can use:
        # os.system(f"notepad {note_file}")
        list_notes()  # Refresh the notes list after editing
    except Exception as e:
        console.print(f"Failed to open note for editing: {e}", style="bold red")


def read_note(note_id):
    note_file = find_note(note_id)
    if not note_file:
        console.print(f"Note '{note_id}' not found.", style="bold red")
        return

    with note_file.open("r") as f:
        content = f.read()

    metadata, note_content = content.split("---\n", 2)[1:]
    metadata = yaml.safe_load(metadata)

    console.print(
        Panel(
            f"[bold cyan]Title:[/bold cyan] {metadata['title']}\n"
            f"[bold green]Created:[/bold green] {metadata['created']}\n"
            f"[bold yellow]Tags:[/bold yellow] {', '.join(metadata['tags']) if metadata['tags'] else 'None'}",
            title="Note Details",
            expand=False,
        )
    )

    console.print(Markdown(note_content))


def list_notes():
    global selected_row
    selected_row = 0
    for file in NOTES_DIR.glob("*.md"):
        with file.open("r") as f:
            content = f.read()
            metadata = yaml.safe_load(content.split("---")[1])
            created_str = (
                metadata["created"].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(metadata["created"], datetime)
                else str(metadata["created"])
            )
            notes.append((file.stem, metadata["title"], created_str))

    while True:
        clear_screen()
        console.print(get_notes_table())
        display_options()
        key = prompt("", key_bindings=create_key_bindings())

        if key == "q":
            break
        elif key == "e":
            selected_note = notes[selected_row][0]
            edit_note(selected_note)
            styled_input = Panel(
                Text(
                    "Press Enter to return to the notes list.",
                    style="bold green on black",
                ),
                border_style="bright_blue",
                expand=False,
            )
            console.print(styled_input)
            input()
        elif key == "r":
            selected_note = notes[selected_row][0]
            # Confirmation prompt_toolkit
            confirm = prompt(
                f"Are you sure you want to delete the note {selected_note}'? (y/n): "
            )
            if confirm.lower() == "y":
                delete_note(selected_note)  # Call the delete functionconsole
                console.print(
                    f"Note '{selected_note}' has been deleted.", style="bold green"
                )
            else:
                console.print("Deletion cancelled.", style="bold yellow")

            styled_input = Panel(
                Text(
                    "Press Enter to return to the notes list.",
                    style="bold green on black",
                ),
                border_style="bright_blue",
                expand=False,
            )
            console.print(styled_input)
            input()  # Wait for Enter key
        elif key == "up":
            selected_row = max(0, selected_row - 1)
        elif key == "down":
            selected_row = min(len(notes) - 1, selected_row + 1)
        elif key == "enter":
            selected_note = notes[selected_row][0]
            read_note(selected_note)
            styled_input = Panel(
                Text(
                    "Press Enter to return to the notes list",
                    style="bold green on black",
                ),
                border_style="bright_blue",
                expand=False,
            )
            console.print(styled_input)
            input()  # Wait for Enter key


def delete_note(note_id):
    for file in NOTES_DIR.glob("*.md"):
        if note_id.lower() in file.stem.lower():
            try:
                os.unlink(file)
                return
            except OSError as e:
                print(f"Error deleting note: {e}")
                return
    print(f"Note '{note_id}' not found.")


def get_notes_table():
    table = Table(title="Your Notes", show_header=True, header_style="bold blue")
    table.add_column("ID", style="dim", width=30)
    table.add_column("Title", style="magenta", width=50)
    table.add_column("Created", style="green", width=20)

    for i, (note_id, title, created) in enumerate(notes):
        row_style = "reverse" if i == selected_row else ""
        table.add_row(
            wrap_text(note_id, 30), wrap_text(title, 50), created, style=row_style
        )
    return table


def show_help():
    commands = [
        ('notes "Title" Content', "Create a new note with quoted title"),
        ("notes", "List all notes"),
        ("todo <description>", "Add a new todo"),
        ("todos", "List all todos"),
        ("complete <id>", "Mark a todo as complete"),
        ("help", "Show this help message"),
        ("exit", "Exit NerdNotes"),
    ]

    table = Table(
        title="Available Commands", show_header=True, header_style="bold cyan"
    )
    table.add_column("Command", style="dim", width=30)
    table.add_column("Description", style="green")

    for command, description in commands:
        table.add_row(command, description)

    console.print(table)


def interactive_mode():
    display_logo()
    print("Welcome to NerdNotes! Type 'help' for available commands.")

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "exit":
            print("Thank you for using NerdNotes!")
            break

        parts = shlex.split(user_input)
        command = parts[0].lower()

        # Manage notes and todos
        if command == "notes":
            if len(parts) == 1:
                list_notes()  # Just show notes
            elif len(parts) > 1:
                title = parts[1]
                content = " ".join(parts[2:]) if len(parts) > 2 else ""
                create_note(title, content)  # Create a new note

        elif command == "todos":
            list_todos()
        elif command == "todo" and len(parts) > 1:
            todo_description = " ".join(parts[1:])
            add_todo(todo_description)
        elif command == "complete" and len(parts) > 1:
            complete_todo(parts[1])
        elif command == "help":
            show_help()
        else:
            print(
                f"Unknown command: '{user_input}'. Type 'help' for available commands."
            )


# Main function
def main():
    parser = argparse.ArgumentParser(
        description="NerdNotes: Integrated Notes and Todos for developers"
    )
    parser.add_argument(
        "action",
        choices=[
            "interactive",
            "list-notes",
            "list-todos",
            "add-todo",
            "complete-todo",
        ],
    )
    parser.add_argument(
        "params", nargs="*", help="Additional parameters for the action"
    )

    args = parser.parse_args()

    if args.action == "interactive":
        interactive_mode()
    elif args.action == "list-notes":
        list_notes()
    elif args.action == "list-todos":
        list_todos()
    elif args.action == "add-todo":
        add_todo(" ".join(args.params))
    elif args.action == "complete-todo":
        complete_todo(args.params[0])


if __name__ == "__main__":
    main()
