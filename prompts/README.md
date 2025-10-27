# Prompts Directory

This directory contains prompt templates for LLM-powered features in quarto4sbp.

## Directory Structure

```
prompts/
├── README.md           # This file
├── tov/                # Tone of Voice prompts
│   ├── system.txt      # System prompt for ToV rewriting
│   └── rewrite-slide.txt  # Slide rewriting prompt template
├── viz/                # Visualization prompts
│   ├── analyze-slide.txt   # Slide analysis for image candidates
│   └── generate-image.txt  # Image generation prompt
└── common/             # Shared prompt components
    └── format-json.txt # JSON formatting instructions
```

## Prompt Organization

Prompts are organized by feature:

- **tov/**: Prompts for tone-of-voice rewriting functionality
- **viz/**: Prompts for visualization and image generation
- **common/**: Reusable prompt components used across features

## File Formats

Prompts can be stored as either:
- `.txt` files (plain text)
- `.md` files (markdown)

Both formats are supported. The prompt loader will try `.txt` first, then `.md`.

## Using Prompts

### Basic Loading

```python
from quarto4sbp.llm.prompts import load_prompt

# Load a prompt
system_prompt = load_prompt("tov/system")
```

### Template Variables

Many prompts support template variables using Python's `{variable}` syntax:

```python
from quarto4sbp.llm.prompts import load_and_format_prompt

# Load and format with variables
prompt = load_and_format_prompt(
    "tov/rewrite-slide",
    tone_guidelines="Be concise and direct",
    slide_content="# My Slide\n- Point 1\n- Point 2"
)
```

### Custom Loader

For testing or custom prompt directories:

```python
from pathlib import Path
from quarto4sbp.llm.prompts import PromptLoader

loader = PromptLoader(prompts_dir=Path("/custom/prompts"))
prompt = loader.load("my-prompt")
```

## Prompt Design Guidelines

When creating new prompts:

1. **Be Specific**: Clearly define the task and expected output
2. **Use Examples**: Show desired output format when possible
3. **Include Context**: Provide relevant background information
4. **Template Variables**: Use `{variable}` syntax for dynamic content
5. **Output Format**: Specify exact format (markdown, JSON, etc.)
6. **Constraints**: List any limitations or requirements
7. **Professional Tone**: Maintain business-appropriate language

## Template Variable Syntax

Use Python string formatting syntax:

```
This is a template with {variable_name}.
You can use multiple {var1} and {var2} variables.
```

Required variables should be documented in comments at the top of the prompt file.

## Adding New Prompts

1. Choose the appropriate category directory (tov, viz, common)
2. Create a `.txt` or `.md` file with a descriptive name
3. Write the prompt following the design guidelines
4. Test with the prompt loader
5. Document any template variables in the file or this README

## Caching

The prompt loader caches loaded prompts by default (LRU cache, max 32 prompts). This improves performance by avoiding repeated file reads.

To clear the cache (useful in testing):

```python
from quarto4sbp.llm.prompts import get_loader

loader = get_loader()
loader.clear_cache()
```

## Common Prompts

The `common/` directory contains reusable prompt fragments that can be referenced or combined with other prompts:

- `format-json.txt`: Instructions for JSON-formatted responses

These can be loaded and combined programmatically as needed.