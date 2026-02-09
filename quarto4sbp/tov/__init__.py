"""Tone of voice rewriting package.

This package provides functionality for rewriting .qmd file content to match
company tone of voice guidelines using LLM.
"""

from quarto4sbp.tov.parser import QmdDocument, parse_qmd
from quarto4sbp.tov.rewriter import rewrite_content
from quarto4sbp.tov.updater import update_file

__all__ = [
    "parse_qmd",
    "QmdDocument",
    "rewrite_content",
    "update_file",
]
