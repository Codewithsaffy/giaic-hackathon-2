---
name: python-clean-code
description: Enforce professional Python standards in all generated code: clear and consistent naming, modular design, single-responsibility functions, type hints, no unnecessary globals, readable formatting (PEP-8), and maintainable structure. Automatically improve or correct code that violates clean-code principles.
---

# Python Clean Code

This skill enforces professional Python standards in all generated code to ensure high-quality, maintainable, and readable Python applications.

## When to Use This Skill

This skill should be used when:
- Generating new Python code to ensure it follows clean code principles
- Reviewing existing Python code for clean code compliance
- Refactoring Python code to improve maintainability
- Teaching or enforcing Python best practices
- Correcting code that violates clean code principles

## Core Principles

### 1. Clear and Consistent Naming
- Use descriptive names for variables, functions, classes, and modules
- Follow Python naming conventions (snake_case for functions/variables, PascalCase for classes)
- Avoid abbreviations unless they're well-known (e.g., HTTP, URL)
- Choose names that reveal intent and make code self-documenting

### 2. Modular Design
- Organize code into logical modules and packages
- Apply the single responsibility principle to modules
- Keep modules focused on a single purpose
- Use imports to connect modules, not tight coupling

### 3. Single-Responsibility Functions
- Each function should have one reason to exist
- Keep functions small and focused (ideally less than 20 lines)
- Extract complex logic into separate functions
- Avoid functions with multiple return points when possible

### 4. Type Hints
- Add type hints to all function signatures
- Use type hints for complex variable assignments
- Leverage typing module for complex types (Union, Optional, List, Dict, etc.)
- Use type hints to improve code readability and IDE support

### 5. No Unnecessary Globals
- Avoid global variables unless absolutely necessary
- Use function parameters and return values instead of global state
- Use class attributes or dependency injection for shared state
- Minimize the global namespace pollution

### 6. Readable Formatting (PEP-8)
- Follow PEP-8 style guide for consistent formatting
- Use proper indentation (4 spaces)
- Limit line length to 79 characters
- Add proper spacing around operators and after commas
- Include docstrings for modules, classes, and functions

### 7. Maintainable Structure
- Organize imports in the standard order (standard library, third-party, local)
- Use meaningful comments only when necessary to explain "why" not "what"
- Separate logical sections with blank lines
- Keep related functions and classes together

## How to Apply Clean Code Principles

### Before Writing Code
1. Plan the function or class structure
2. Identify the single responsibility
3. Choose descriptive names
4. Consider type hints for inputs and outputs

### During Implementation
1. Write small, focused functions
2. Add type hints to all function signatures
3. Follow PEP-8 formatting guidelines
4. Add meaningful docstrings
5. Avoid global variables

### During Review
1. Check for adherence to naming conventions
2. Verify functions have single responsibility
3. Confirm type hints are present and correct
4. Look for unnecessary global variables
5. Ensure code follows PEP-8 formatting
6. Assess overall maintainability and readability

## Common Clean Code Violations to Avoid

- Functions longer than 20 lines
- Functions with more than 3-4 parameters
- Missing type hints in function signatures
- Global variables used for state
- Inconsistent or unclear naming
- Code without proper documentation
- Deep nesting (more than 3 levels)
- Complex conditionals that could be simplified

## How to Improve Code That Violates Clean Code Principles

1. **Large Functions**: Break them into smaller, single-responsibility functions
2. **Missing Type Hints**: Add appropriate type annotations
3. **Global Variables**: Pass values as parameters or use dependency injection
4. **Unclear Naming**: Rename to be more descriptive
5. **Poor Formatting**: Reformat to follow PEP-8
6. **Missing Documentation**: Add appropriate docstrings and comments
7. **Complex Conditionals**: Extract to named functions or use guard clauses
8. **Deep Nesting**: Use early returns or extract nested code to functions

## Validation Checklist

Before finalizing any Python code, ensure it meets these criteria:

- [ ] Functions have clear, descriptive names
- [ ] All functions have type hints for parameters and return values
- [ ] Functions follow single-responsibility principle
- [ ] No unnecessary global variables are used
- [ ] Code follows PEP-8 formatting standards
- [ ] Proper docstrings are included for modules, classes, and functions
- [ ] Import statements are organized properly
- [ ] Code is modular and well-organized
- [ ] No complex nested structures (max 3 levels)
- [ ] Comments explain "why" not "what" when present