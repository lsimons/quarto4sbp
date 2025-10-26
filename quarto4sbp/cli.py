"""CLI entry point for q4s (quarto4sbp) tool."""

import argparse
import sys

from quarto4sbp.commands import cmd_echo, cmd_help, cmd_new_pptx, cmd_pdf_pptx


def main(args: list[str] | None = None) -> int:
    """Main entry point for q4s CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    parser = argparse.ArgumentParser(
        prog="q4s",
        description="quarto4sbp CLI tool",
        add_help=False,  # We handle help ourselves
    )

    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run (help, echo, new-pptx, pdf-pptx)",
    )

    parser.add_argument(
        "command_args",
        nargs="*",
        help="Arguments for the command",
    )

    parsed = parser.parse_args(args)

    command = parsed.command
    command_args = parsed.command_args

    # Default to help if no command provided
    if command is None:
        return cmd_help()

    # Route to appropriate subcommand
    if command == "help":
        return cmd_help()
    elif command == "echo":
        return cmd_echo(command_args)
    elif command == "new-pptx":
        return cmd_new_pptx(command_args)
    elif command == "pdf-pptx":
        return cmd_pdf_pptx(command_args)
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        print("Run 'q4s help' for usage information", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
