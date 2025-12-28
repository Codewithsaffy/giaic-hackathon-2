---
name: cli-app
description: Apply best practices for command-line applications: clear command flow, user-friendly prompts and messages, logical separation of concerns (models, business logic, interface), predictable command behavior, and scalable project structure suitable for small and large CLI tools.
---

# CLI Application Architecture

This skill provides best practices for designing and building command-line applications with a focus on maintainability, user experience, and scalability.

## When to Use This Skill

This skill should be used when:
- Designing a new command-line application
- Refactoring an existing CLI application for better architecture
- Improving user experience in CLI tools
- Scaling a small CLI tool to handle more complex functionality
- Establishing consistent patterns across CLI projects

## Core Principles

### 1. Clear Command Flow
- Design intuitive command hierarchies (e.g., `app user create`, `app user delete`)
- Provide clear help messages for each command level
- Use consistent command naming conventions
- Implement proper command validation and error handling
- Follow the principle of least surprise for command behavior

### 2. User-Friendly Prompts and Messages
- Provide clear, actionable error messages
- Use appropriate verbosity levels (quiet, normal, verbose)
- Implement progress indicators for long-running operations
- Support colored output when appropriate
- Include helpful examples in help text
- Use consistent formatting for all user-facing messages

### 3. Logical Separation of Concerns
- **Models**: Data structures and validation logic
- **Business Logic**: Core application functionality and rules
- **Interface**: CLI-specific code (arguments, options, output formatting)
- Keep dependencies flowing from interface → business logic → models
- Ensure each layer has a single responsibility
- Use dependency injection where appropriate for testability

### 4. Predictable Command Behavior
- Follow established CLI conventions (e.g., flags, positional arguments)
- Implement consistent exit codes (0 for success, non-zero for errors)
- Handle signals gracefully (SIGINT, SIGTERM)
- Provide dry-run options where appropriate
- Maintain consistent argument parsing behavior

### 5. Scalable Project Structure
- Organize commands in a hierarchical directory structure
- Use a command router/dispatcher pattern
- Implement plugin architecture for extensibility
- Separate configuration management
- Support for multiple environments/profiles

## Recommended Project Structure

```
my-cli-app/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Entry point and argument parsing
│   ├── commands/            # Individual command modules
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── ...
│   ├── core/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── models/          # Data models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── ...
│   │   ├── services/        # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   └── ...
│   │   └── config.py        # Configuration management
│   ├── utils/               # Helper functions
│   │   ├── __init__.py
│   │   └── formatting.py
│   └── exceptions.py        # Custom exceptions
├── tests/
├── setup.py                 # Package definition
└── README.md
```

## Command Implementation Pattern

### Basic Command Structure
```python
import argparse
from typing import Any
from cli.core.base_command import BaseCommand
from cli.core.exceptions import CLIException

class MyCommand(BaseCommand):
    """Description of what this command does."""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments to the parser."""
        parser.add_argument(
            "required_arg",
            help="Description of required argument"
        )
        parser.add_argument(
            "-o", "--optional",
            help="Description of optional argument"
        )

    def execute(self, args: argparse.Namespace) -> Any:
        """Execute the command with provided arguments."""
        try:
            # Business logic here
            result = self.handle_logic(args)
            self.print_result(result)
            return 0  # Success exit code
        except CLIException as e:
            self.error(str(e))
            return 1  # Error exit code
```

### Command Registration
```python
# In cli/commands/__init__.py
from .user import UserCommand
from .project import ProjectCommand

COMMANDS = {
    'user': UserCommand,
    'project': ProjectCommand,
    # Add more commands here
}
```

## Best Practices for CLI Design

### 1. Argument and Option Handling
- Use short and long forms for options (e.g., `-v` and `--verbose`)
- Follow common flag conventions (e.g., `-h` for help, `-v` for verbose)
- Validate arguments early and provide clear error messages
- Support file input/output via stdin/stdout when appropriate
- Use `--` to separate options from positional arguments when needed

### 2. Configuration Management
- Support configuration files (e.g., `.mycliapp/config`)
- Allow environment variable overrides
- Implement profile support for multiple configurations
- Provide command to manage configuration settings
- Use secure storage for sensitive information

### 3. Output Formatting
- Support different output formats (text, JSON, CSV)
- Implement proper exit codes for different scenarios
- Use appropriate output streams (stdout for data, stderr for errors)
- Support quiet mode to suppress non-essential output
- Include machine-readable output options for scripting

### 4. Testing Strategy
- Unit test business logic separately from CLI interface
- Integration test command flows
- Test argument parsing and validation
- Mock external dependencies for faster tests
- Test error conditions and help text

## Error Handling and Exit Codes

### Standard Exit Codes
- 0: Success
- 1: General error
- 2: Misuse of shell command (e.g., wrong arguments)
- 126: Command cannot execute
- 127: Command not found
- 128+n: Fatal error signal "n"

### Error Message Guidelines
- Start with a clear error type prefix
- Provide actionable information to resolve the issue
- Include relevant context (file paths, command, etc.)
- Suggest alternative approaches when possible
- Use consistent formatting across all errors

## Scalability Considerations

### For Growing Applications
- Implement command plugins/extensions
- Use dependency injection for testability
- Separate domain logic from CLI concerns
- Implement caching for expensive operations
- Support for command aliases
- Configuration profiles for different environments

### Performance Optimization
- Lazy loading of command modules
- Efficient argument parsing
- Caching of configuration and state
- Asynchronous operations where appropriate
- Memory-efficient processing of large datasets

## Common CLI Patterns

### Subcommand Pattern
```
app resource action [options]
app user create --name "John" --email "john@example.com"
app user list --format json
```

### Configuration Commands
```
app config set api_key=12345
app config get api_key
app config list
```

### Help and Documentation
- Comprehensive help at every level
- Inline examples in help text
- Dedicated documentation commands
- Version information accessible via `--version`

## Validation Checklist

Before finalizing any CLI application, ensure it meets these criteria:

- [ ] Command structure is intuitive and follows conventions
- [ ] Help messages are clear and comprehensive
- [ ] Error messages are actionable and user-friendly
- [ ] Exit codes follow standard conventions
- [ ] Arguments and options follow common patterns
- [ ] Output is properly formatted and configurable
- [ ] Configuration management is implemented
- [ ] Tests cover command flows and error conditions
- [ ] Architecture separates concerns appropriately
- [ ] Project structure supports future growth