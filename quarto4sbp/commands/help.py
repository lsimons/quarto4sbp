"""Help command for q4s CLI."""


def cmd_help() -> int:
    """Handle the help subcommand.

    Returns:
        Exit code (0 for success)
    """
    print("q4s - quarto4sbp CLI tool")
    print()
    print("Usage: q4s <command> [arguments]")
    print()
    print("Available commands:")
    print("  help       Show this help message")
    print("  echo       Echo back the command-line arguments")
    print("  new        Create a new Quarto presentation from template")
    print("  pdf        Export PowerPoint presentations to PDF")
    print()
    print("Examples:")
    print("  q4s help")
    print("  q4s echo hello world")
    print("  q4s new my-presentation")
    print(
        "  q4s pdf                    # Export all stale PPTX files in current directory"
    )
    return 0
