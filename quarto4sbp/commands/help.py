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
    print()
    print("PowerPoint commands:")
    print("  new-pptx   Create a new Quarto PowerPoint presentation from template")
    print("  pdf-pptx   Export PowerPoint presentations to PDF (when PPTX is newer)")
    print()
    print("Word commands:")
    print("  new-doc    Create a new Quarto Word document from template")
    print("  pdf-doc    Export Word documents to PDF (when DOCX is newer)")
    print()
    print("Unified commands:")
    print("  pdf        Export all Office documents (PPTX and DOCX) to PDF")
    print()
    print("Examples:")
    print("  q4s help")
    print("  q4s echo hello world")
    print()
    print("  # Create new documents:")
    print("  q4s new-pptx my-presentation")
    print("  q4s new-doc my-document")
    print()
    print("  # Export to PDF:")
    print(
        "  q4s pdf                    # Export all Office documents in current directory"
    )
    print("  q4s pdf-pptx               # Export only PowerPoint files")
    print("  q4s pdf-doc                # Export only Word documents")
    return 0
