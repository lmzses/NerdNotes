# NerdNotes

Welcome to **NerdNotes**, a command-line-based note-taking and to-do management application! NerdNotes allows you to create, edit, and manage your notes and to-dos efficiently from the terminal.

## Features

- **Create, Read, Edit, and Delete Notes**: Organize your thoughts and ideas in markdown notes.
- **To-Do Management**: Create, mark as complete/incomplete, edit, and delete your to-dos.
- **Interactive Command-Line Interface**: Easy-to-use commands to manage your notes and to-dos.
- **Tagging and Prioritization**: Tag your notes and prioritize your to-dos for better organization.

## Note

This is the first version of NerdNotes, and many features or commands are still under development.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/lmzses/nerdnotes.git
   cd NerdNotes
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the `ndnotes.py` script to start the application:

```bash
python ndnotes.py
```

Once the application is running, you can use the following commands:

### Notes Commands

- **Create a Note**:

  ```bash
  create <note_title>
  ```

  Example: `create My First Note`

- **Read a Note**:

  ```bash
  read <note_id>
  ```

  Example: `read 20230711_123456`

- **Edit a Note**:

  ```bash
  edit <note_id>
  ```

  Example: `edit 20230711_123456`

- **Delete a Note**:

  ```bash
  delete <note_id>
  ```

  Example: `delete 20230711_123456`

- **List All Notes**:
  ```bash
  notes
  ```

### To-Do Commands

- **Create a To-Do**:

  ```bash
  create_todo <description> --due <due_date> --priority <priority> --tags <tags>
  ```

  Example: `create_todo "Finish the project" --due "2023-07-12" --priority "High" --tags "work,urgent"`

- **Mark a To-Do as Complete**:

  ```bash
  complete_todo <todo_id>
  ```

  Example: `complete_todo 1`

- **Edit a To-Do**:

  ```bash
  edit_todo <todo_id> --description <description> --due <due_date> --priority <priority> --tags <tags>
  ```

  Example: `edit_todo 1 --description "Finish the final report"`

- **Delete a To-Do**:

  ```bash
  delete_todo <todo_id>
  ```

  Example: `delete_todo 1`

- **List All To-Dos**:
  ```bash
  todos
  ```

### Help Command

- **Display Help**:
  ```bash
  help
  ```

## Storage

The notes and to-dos are stored in the user's home directory under the folder `.nerdnotes`:

- Notes are saved in `~/.nerdnotes/notes/`
- To-Dos are saved in `~/.nerdnotes/todos/todos.txt`

## Project Structure

```
NerdNotes/
├── ndnotes.py
├── requirements.txt
└── README.md
```

- `ndnotes.py`: Main application script.
- `requirements.txt`: List of dependencies.
- `README.md`: Project documentation.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the simplicity of command-line tools.
- Thanks to the contributors and the open-source community.

## To-Do

Here are some features that are planned for future versions:

- Implement tagging and prioritization for notes.
- Add search functionality for notes and to-dos.
- Improve the user interface and error handling.
- Add support for recurring to-dos.
- Enhance the help command with more detailed information.
- Add unit tests for better code coverage.
