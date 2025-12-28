# 📝 Advanced CLI Todo Application

A beautiful, feature-rich command-line task management application with an intuitive interface and powerful features.

![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎨 Beautiful User Interface
- **ASCII Art Banner** with colorful design
- **Rich Formatting** with icons, emojis, and color-coded elements
- **Interactive Dashboard** showing statistics and progress
- **Formatted Tables** with clean borders and styling
- **Progress Bars** for visual task completion tracking

### 📊 Task Management
- ✅ Create, Read, Update, Delete tasks
- 🎯 **Priority Levels**: High (🔴), Medium (🟡), Low (🟢)
- 📅 **Due Dates** with smart parsing (tomorrow, next week, specific dates)
- 🏷️ **Categories** for organization
- #️⃣ **Tags** for additional labeling
- ⏰ **Timestamps** (created_at, updated_at)
- ✔️ Toggle completion status

### 🔍 Advanced Features
- **Search**: Find tasks by title or description
- **Filter**: By priority, category, status, or overdue
- **Sort**: By priority, due date, or creation date
- **Statistics**: Completion percentage, priority breakdown, category breakdown
- **Overdue Tracking**: Automatic detection and warnings
- **Upcoming Tasks**: See tasks due soon

### 💾 Data Persistence
- **Auto-Save**: Tasks automatically saved to JSON file
- **Auto-Load**: Previous tasks loaded on startup
- **Storage Location**: `~/.todo/tasks.json`

## 📦 Installation

### Prerequisites
- Python 3.13 or higher
- pip package manager

### Steps

1. **Clone or download the repository**

2. **Navigate to the project directory**
   ```bash
   cd phase-1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Interactive Menu Mode (Recommended)

Start the application:
```bash
python -m src.main
```

You'll see a beautiful welcome banner and interactive menu with these options:

```
1. 📝 Add Task         - Create a new task
2. 📋 View All Tasks   - Display all tasks in a table
3. 📊 Dashboard        - View statistics and analytics
4. 🔍 Search Tasks     - Search tasks by keyword
5. 🎯 Filter Tasks     - Filter by category, priority, or status
6. 👁️  View Task Details - Show detailed task information
7. ✏️  Update Task     - Modify task properties
8. ✅ Toggle Complete  - Mark task as complete/incomplete
9. 🗑️  Delete Task     - Remove a task
0. 🚪 Exit            - Exit the application
```

### Command Line Mode

You can also use direct commands:

```bash
# Add a task
python -m src.cli add "Complete project" --priority high

# List all tasks
python -m src.cli list

# Show dashboard
python -m src.cli dashboard

# Search tasks
python -m src.cli search "project"

# Show task details
python -m src.cli show 1

# Mark task complete
python -m src.cli complete 1

# Delete a task
python -m src.cli delete 1
```

## 📖 Examples

### Creating a Task with All Features

When you select "Add Task" from the menu:

1. **Title**: "Complete hackathon project"
2. **Description**: "Finish all features and test thoroughly"
3. **Priority**: High (🔴)
4. **Category**: "Work"
5. **Due Date**: "tomorrow" (or "2025-12-31", "next week", etc.)
6. **Tags**: "urgent, coding, hackathon"

### Viewing Dashboard

The dashboard shows:
- 📊 Total tasks, completed, pending, overdue
- Progress bar with completion percentage
- Priority breakdown (High/Medium/Low)
- Category breakdown
- List of overdue tasks
- Upcoming tasks (next 7 days)

### Searching and Filtering

- **Search**: Find tasks containing "hackathon"
- **Filter by Priority**: Show only High priority tasks
- **Filter by Category**: Show "Work" category tasks
- **Filter by Status**: Show completed or pending tasks
- **Show Overdue**: Display all overdue tasks

## 🎯 Smart Date Parsing

The app supports flexible date input:
- **Relative**: `today`, `tomorrow`, `next week`, `next month`
- **Specific**: `2025-12-31`, `Dec 31`, `December 31, 2025`
- **Fuzzy**: Any natural date format

## 🏗️ Project Structure

```
phase-1/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Entry point
│   ├── cli.py               # CLI commands and menu
│   ├── models.py            # Task and Priority models
│   ├── store.py             # Data storage and persistence
│   ├── ui_components.py     # UI elements (banner, tables, etc.)
│   └── utils.py             # Helper functions
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project metadata
└── README.md               # This file
```

## 🔧 Dependencies

- **typer**: CLI framework
- **rich**: Terminal formatting and styling
- **python-dateutil**: Advanced date parsing
- **pyfiglet**: ASCII art generation
- **questionary**: Interactive prompts

## 💡 Tips & Tricks

1. **Keyboard Shortcuts**: Use Ctrl+C to cancel any operation
2. **Date Flexibility**: Use natural language for due dates
3. **Category Autocomplete**: Existing categories are suggested
4. **Tag Format**: Separate multiple tags with commas
5. **Priority Colors**: Tasks are color-coded by priority for easy scanning

## 🐛 Troubleshooting

### Tasks not saving
- Check write permissions for `~/.todo/` directory
- Ensure sufficient disk space

### Application won't start
- Verify Python version: `python --versionshould be 3.13+
- Reinstall dependencies: `pip install -r requirements.txt`

### UI looks broken
- Make sure terminal supports Unicode and colors
- Try a different terminal emulator

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 🎉 Acknowledgments

Built with ❤️ using Python and modern CLI libraries.

---

**Happy Task Management! 📝✨**
