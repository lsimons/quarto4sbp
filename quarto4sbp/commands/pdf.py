"""Unified PDF export command for both PowerPoint and Word documents."""

from quarto4sbp.commands.pdf_pptx import cmd_pdf_pptx
from quarto4sbp.commands.pdf_docx import cmd_pdf_docx


def cmd_pdf(args: list[str]) -> int:
    """Handle the unified pdf subcommand.

    Exports both PowerPoint (.pptx) and Word (.docx) files to PDF.

    Args:
        args: Optional directory argument (defaults to current directory)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    print("=== Exporting PowerPoint files ===")
    pptx_result = cmd_pdf_pptx(args)

    print("\n=== Exporting Word documents ===")
    doc_result = cmd_pdf_docx(args)

    # Return success only if both succeed
    if pptx_result == 0 and doc_result == 0:
        print("\n✓ All exports completed successfully")
        return 0
    else:
        print("\n✗ Some exports failed")
        return 1
