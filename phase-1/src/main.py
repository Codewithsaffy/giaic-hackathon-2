import sys
import platform
from typing import NoReturn

# Import the main_menu function from cli module
try:
    from .cli import main_menu
except ImportError:
    from cli import main_menu


def check_python_version() -> bool:
    """
    Verify that the Python version is 3.13 or higher.

    Returns:
        bool: True if Python version is 3.13+, False otherwise
    """
    major, minor, _ = sys.version_info[:3]
    return major == 3 and minor >= 13


def main() -> NoReturn:
    """
    Main entry point for the CLI Todo application.

    Verifies Python 3.13+ requirement and starts the main menu loop.
    """
    if not check_python_version():
        print(f"Error: This application requires Python 3.13 or higher.")
        print(f"Current Python version: {platform.python_version()}")
        sys.exit(1)

    print(f"Python {platform.python_version()} detected. Starting CLI Todo Application...")

    # Start the main menu loop
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()