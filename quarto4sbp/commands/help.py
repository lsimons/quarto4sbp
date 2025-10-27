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
    print()
    print("LLM commands:")
    print("  llm test   Test LLM connectivity and configuration")
    print("  tov        Rewrite .qmd files to match company tone of voice")
    print()
    print("PowerPoint commands:")
    print("  new-pptx   Create a new Quarto PowerPoint presentation from template")
    print("  pdf-pptx   Export PowerPoint presentations to PDF (when PPTX is newer)")
    print()
    print("Word commands:")
    print("  new-docx   Create a new Quarto Word document from template")
    print("  pdf-docx   Export Word documents to PDF (when DOCX is newer)")
    print()
    print("Unified commands:")
    print("  new        Create both PowerPoint and Word documents from templates")
    print("  pdf        Export all Office documents (PPTX and DOCX) to PDF")
    print()
    print("Examples:")
    print("  q4s help")
    print()
    print("  # Test LLM integration:")
    print("  q4s llm test")
    print()
    print("  # Rewrite content to match tone of voice:")
    print("  q4s tov my-presentation/my-presentation.qmd")
    print("  q4s tov my-presentation/ --dry-run")
    print()
    print("  # Create new documents:")
    print("  q4s new my-project          # Create both PPTX and DOCX")
    print("  q4s new-pptx my-presentation")
    print("  q4s new-docx my-document")
    print()
    print("  # Export to PDF:")
    print(
        "  q4s pdf                    # Export all Office documents in current directory"
    )
    print("  q4s pdf-pptx               # Export only PowerPoint files")
    print("  q4s pdf-docx               # Export only Word documents")
    return 0
