"""QMD parser for extracting and preserving document structure.

This module parses Quarto Markdown (.qmd) files into structured components,
separating YAML frontmatter, code blocks, and markdown content for selective
rewriting while preserving the original structure.
"""

import re
from dataclasses import dataclass


@dataclass
class QmdSection:
    """A section of markdown content to be rewritten.

    Attributes:
        content: The markdown content of this section
        start_line: Starting line number in original file
        end_line: Ending line number in original file
        level: Heading level (1-6) if this section starts with a heading
    """

    content: str
    start_line: int
    end_line: int
    level: int | None = None


@dataclass
class QmdDocument:
    """Parsed QMD document structure.

    Attributes:
        yaml_frontmatter: YAML frontmatter content (with --- delimiters)
        sections: List of markdown sections to rewrite
        full_content: Original full content of the file
        line_endings: Line ending style ('\n' or '\r\n')
    """

    yaml_frontmatter: str
    sections: list[QmdSection]
    full_content: str
    line_endings: str = "\n"


def parse_qmd(content: str) -> QmdDocument:
    """Parse a QMD file into structured components.

    This function:
    1. Extracts YAML frontmatter (preserves as-is)
    2. Identifies code blocks (preserves as-is)
    3. Splits remaining content into sections by headings
    4. Preserves inline code (backtick-delimited)

    Args:
        content: Full content of the .qmd file

    Returns:
        QmdDocument with parsed structure
    """
    # Detect line endings
    line_endings = "\r\n" if "\r\n" in content else "\n"

    # Split into lines
    lines = content.splitlines(keepends=True)

    # Extract YAML frontmatter
    yaml_end_line = 0
    yaml_frontmatter = ""

    if lines and lines[0].strip() == "---":
        # Find closing ---
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                yaml_end_line = i + 1
                yaml_frontmatter = "".join(lines[0:yaml_end_line])
                break

    # Process content after YAML
    content_lines = lines[yaml_end_line:]

    # Build sections while preserving code blocks
    sections: list[QmdSection] = []
    current_section_lines: list[str] = []
    current_section_start = yaml_end_line
    in_code_block = False
    code_fence_pattern = re.compile(r"^```|^~~~")

    for i, line in enumerate(content_lines):
        line_num = yaml_end_line + i

        # Track code block boundaries
        if code_fence_pattern.match(line):
            in_code_block = not in_code_block
            current_section_lines.append(line)
            continue

        # If in code block, just accumulate
        if in_code_block:
            current_section_lines.append(line)
            continue

        # Check for heading (only outside code blocks)
        heading_match = re.match(r"^(#{1,6})\s+(.+)", line)

        if heading_match:
            # Save previous section if exists
            if current_section_lines:
                section_content = "".join(current_section_lines)
                if section_content.strip():  # Only save non-empty sections
                    sections.append(
                        QmdSection(
                            content=section_content,
                            start_line=current_section_start,
                            end_line=line_num - 1,
                            level=None,
                        )
                    )

            # Start new section with heading
            current_section_lines = [line]
            current_section_start = line_num
        else:
            current_section_lines.append(line)

    # Save final section
    if current_section_lines:
        section_content = "".join(current_section_lines)
        if section_content.strip():
            sections.append(
                QmdSection(
                    content=section_content,
                    start_line=current_section_start,
                    end_line=len(lines) - 1,
                    level=None,
                )
            )

    # If no sections found (no headings), treat entire content as one section
    if not sections and content_lines:
        all_content = "".join(content_lines)
        if all_content.strip():
            sections.append(
                QmdSection(
                    content=all_content,
                    start_line=yaml_end_line,
                    end_line=len(lines) - 1,
                    level=None,
                )
            )

    return QmdDocument(
        yaml_frontmatter=yaml_frontmatter,
        sections=sections,
        full_content=content,
        line_endings=line_endings,
    )


def reconstruct_qmd(doc: QmdDocument, rewritten_sections: list[str]) -> str:
    """Reconstruct a QMD file from frontmatter and rewritten sections.

    Args:
        doc: Original parsed QMD document
        rewritten_sections: List of rewritten section contents (same order as doc.sections)

    Returns:
        Complete QMD file content with rewritten sections

    Raises:
        ValueError: If number of rewritten sections doesn't match original
    """
    if len(rewritten_sections) != len(doc.sections):
        raise ValueError(
            f"Mismatch: {len(rewritten_sections)} rewritten sections "
            f"but {len(doc.sections)} original sections"
        )

    # Start with YAML frontmatter
    parts = [doc.yaml_frontmatter] if doc.yaml_frontmatter else []

    # Add rewritten sections
    for rewritten in rewritten_sections:
        parts.append(rewritten)

    # Join with original line endings
    result = "".join(parts)

    # Ensure file ends with newline if original did
    if doc.full_content.endswith(("\n", "\r\n")) and not result.endswith(
        ("\n", "\r\n")
    ):
        result += doc.line_endings

    return result
