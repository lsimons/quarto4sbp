"""CLI entry point for q4s (quarto4sbp) tool."""

import argparse
import sys

from quarto4sbp.commands import (
    cmd_help,
    cmd_llm,
    cmd_new,
    cmd_new_docx,
    cmd_new_pptx,
    cmd_pdf,
    cmd_pdf_docx,
    cmd_pdf_pptx,
    cmd_tov,
)


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
        help="Command to run (help, llm, new, new-pptx, new-docx, pdf, pdf-pptx, pdf-docx, tov)",
    )

    parser.add_argument(
        "command_args",
        nargs="*",
        help="Arguments for the command",
    )

    parsed, unknown = parser.parse_known_args(args)

    command = parsed.command
    # Combine parsed command_args with unknown args to pass to subcommand
    command_args = parsed.command_args + unknown

    # Default to help if no command provided
    if command is None:
        return cmd_help()

    # Route to appropriate subcommand
    if command == "help":
        return cmd_help()
    elif command == "llm":
        return cmd_llm(command_args)
    elif command == "new":
        return cmd_new(command_args)
    elif command == "new-pptx":
        return cmd_new_pptx(command_args)
    elif command == "new-docx":
        return cmd_new_docx(command_args)
    elif command == "pdf":
        return cmd_pdf(command_args)
    elif command == "pdf-pptx":
        return cmd_pdf_pptx(command_args)
    elif command == "pdf-docx":
        return cmd_pdf_docx(command_args)
    elif command == "tov":
        return cmd_tov(command_args)
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        print("Run 'q4s help' for usage information", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
