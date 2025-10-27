"""Tests for QMD parser."""

import unittest

from quarto4sbp.tov.parser import parse_qmd, reconstruct_qmd


class TestParseQmd(unittest.TestCase):
    """Test QMD parsing functionality."""

    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        doc = parse_qmd("")
        self.assertEqual(doc.yaml_frontmatter, "")
        self.assertEqual(len(doc.sections), 0)
        self.assertEqual(doc.full_content, "")

    def test_parse_yaml_only(self):
        """Test parsing a file with only YAML frontmatter."""
        content = """---
title: "Test"
---
"""
        doc = parse_qmd(content)
        self.assertEqual(doc.yaml_frontmatter, content)
        self.assertEqual(len(doc.sections), 0)

    def test_parse_simple_content(self):
        """Test parsing simple markdown content without headings."""
        content = """---
title: "Test"
---

This is a paragraph.

This is another paragraph.
"""
        doc = parse_qmd(content)
        self.assertIn('title: "Test"', doc.yaml_frontmatter)
        self.assertEqual(len(doc.sections), 1)
        self.assertIn("This is a paragraph.", doc.sections[0].content)

    def test_parse_with_headings(self):
        """Test parsing content with multiple headings."""
        content = """---
title: "Test"
---

# Introduction

This is the intro.

## Section One

Content for section one.

## Section Two

Content for section two.
"""
        doc = parse_qmd(content)
        self.assertEqual(len(doc.sections), 3)
        self.assertIn("# Introduction", doc.sections[0].content)
        self.assertIn("## Section One", doc.sections[1].content)
        self.assertIn("## Section Two", doc.sections[2].content)

    def test_parse_code_blocks_preserved(self):
        """Test that code blocks are preserved in sections."""
        content = """---
title: "Test"
---

# Code Example

Here is some code:

```python
def hello():
    print("world")
```

End of section.
"""
        doc = parse_qmd(content)
        self.assertEqual(len(doc.sections), 1)
        self.assertIn("```python", doc.sections[0].content)
        self.assertIn("def hello():", doc.sections[0].content)

    def test_parse_code_blocks_with_tildes(self):
        """Test that tilde code blocks are also preserved."""
        content = """# Test

~~~python
code here
~~~

Text after.
"""
        doc = parse_qmd(content)
        self.assertIn("~~~python", doc.sections[0].content)
        self.assertIn("code here", doc.sections[0].content)

    def test_parse_inline_code_preserved(self):
        """Test that inline code is preserved."""
        content = """# Test

Use `code` like this.
"""
        doc = parse_qmd(content)
        self.assertIn("`code`", doc.sections[0].content)

    def test_line_endings_unix(self):
        """Test detection of Unix line endings."""
        content = "---\ntitle: Test\n---\n\nContent\n"
        doc = parse_qmd(content)
        self.assertEqual(doc.line_endings, "\n")

    def test_line_endings_windows(self):
        """Test detection of Windows line endings."""
        content = "---\r\ntitle: Test\r\n---\r\n\r\nContent\r\n"
        doc = parse_qmd(content)
        self.assertEqual(doc.line_endings, "\r\n")

    def test_no_yaml_frontmatter(self):
        """Test parsing content without YAML frontmatter."""
        content = """# Just Content

No YAML here.
"""
        doc = parse_qmd(content)
        self.assertEqual(doc.yaml_frontmatter, "")
        self.assertEqual(len(doc.sections), 1)
        self.assertIn("# Just Content", doc.sections[0].content)

    def test_multiline_yaml_preserved(self):
        """Test that multi-line YAML values are preserved."""
        content = """---
title: "Test"
description: |
  This is a multi-line
  description value
---

# Content
"""
        doc = parse_qmd(content)
        self.assertIn("description: |", doc.yaml_frontmatter)
        self.assertIn("multi-line", doc.yaml_frontmatter)


class TestReconstructQmd(unittest.TestCase):
    """Test QMD reconstruction functionality."""

    def test_reconstruct_simple(self):
        """Test reconstructing a simple QMD file."""
        original = """---
title: "Test"
---

# Section

Content here.
"""
        doc = parse_qmd(original)
        rewritten = ["# Section\n\nRewritten content.\n"]
        result = reconstruct_qmd(doc, rewritten)

        self.assertIn('title: "Test"', result)
        self.assertIn("Rewritten content", result)

    def test_reconstruct_preserves_yaml(self):
        """Test that reconstruction preserves YAML exactly."""
        original = """---
title: "Test"
format:
  pptx:
    reference-doc: template.pptx
---

Content
"""
        doc = parse_qmd(original)
        rewritten = ["Rewritten content\n"]
        result = reconstruct_qmd(doc, rewritten)

        self.assertIn('title: "Test"', result)
        self.assertIn("reference-doc: template.pptx", result)

    def test_reconstruct_mismatch_error(self):
        """Test error when section count doesn't match."""
        original = """# Section One

Content

# Section Two

More content
"""
        doc = parse_qmd(original)
        rewritten = ["Only one section"]  # Should be 2

        with self.assertRaises(ValueError) as ctx:
            reconstruct_qmd(doc, rewritten)

        self.assertIn("Mismatch", str(ctx.exception))

    def test_reconstruct_preserves_line_endings(self):
        """Test that reconstruction preserves line ending style."""
        original = "---\r\ntitle: Test\r\n---\r\n\r\nContent\r\n"
        doc = parse_qmd(original)
        rewritten = ["Rewritten\r\n"]
        result = reconstruct_qmd(doc, rewritten)

        # Should preserve Windows line endings
        self.assertIn("\r\n", result)

    def test_reconstruct_no_yaml(self):
        """Test reconstruction without YAML frontmatter."""
        original = """# Section

Content
"""
        doc = parse_qmd(original)
        rewritten = ["# Section\n\nNew content\n"]
        result = reconstruct_qmd(doc, rewritten)

        self.assertEqual(result, "# Section\n\nNew content\n")

    def test_reconstruct_ensures_final_newline(self):
        """Test that final newline is added if original had one."""
        original = "# Test\n\nContent\n"
        doc = parse_qmd(original)
        rewritten = ["# Test\n\nRewritten"]  # Missing final newline
        result = reconstruct_qmd(doc, rewritten)

        self.assertTrue(result.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
