"""Echo command for q4s CLI."""


def cmd_echo(args: list[str]) -> int:
    """Handle the echo subcommand.

    Args:
        args: Arguments to echo back

    Returns:
        Exit code (0 for success)
    """
    print(" ".join(args))
    return 0
