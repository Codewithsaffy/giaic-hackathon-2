<!-- SYNC IMPACT REPORT:
Version change: N/A (initial creation) → 1.0.0
Modified principles: N/A
Added sections: Code Structure, Style, Tech Stack, Quality, Documentation principles
Removed sections: N/A
Templates requiring updates: N/A
Follow-up TODOs: None
-->
# Python CLI Application Constitution

## Core Principles

### Code Structure
All source code must reside in a `/src` folder. This ensures a clear project organization where all application code is centralized in a single location, making it easier to navigate, maintain, and deploy.

### Style
Follow PEP 8 guidelines, use Type Hints for all functions, and include Docstrings. This ensures code consistency, readability, and maintainability across the project. Type hints improve IDE support and catch errors early, while docstrings provide essential documentation for all functions and classes.

### Tech Stack
Enforce Python 3.13+ and use `uv` for dependency management. This ensures the project uses modern Python features and maintains consistent, fast dependency management across all development and deployment environments.

### Quality
Code must be modular; separate the data model, business logic, and CLI interface. This ensures proper separation of concerns, making the application more maintainable, testable, and extensible. Each component should have a single responsibility and clear interfaces between layers.

### Documentation
Ensure README.md includes setup instructions and CLAUDE.md is maintained. This ensures new developers can quickly get started and all project-specific instructions and guidelines are properly documented for ongoing maintenance and development.

## Additional Constraints

All Python code must follow the clean code principles as defined in the python-clean-code skill, ensuring professional standards in naming, formatting, and structure. CLI applications must follow the architecture patterns defined in the cli-app-architecture skill for predictable, user-friendly command behavior.

## Development Workflow

The development workflow must include:
- Code reviews for all pull requests
- Automated testing for all new features
- Documentation updates for any user-facing changes
- Adherence to the project's architectural principles

## Governance

This constitution defines the mandatory practices for this Python CLI application project. All code contributions must comply with these principles. Deviations require explicit approval and documentation of the rationale. The constitution may only be amended through the established change process, with proper justification and approval.

**Version**: 1.0.0 | **Ratified**: 2025-12-28 | **Last Amended**: 2025-12-28