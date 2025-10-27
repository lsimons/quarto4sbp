"""LLM test command for verifying connectivity and configuration.

This command tests the LLM integration by:
- Loading configuration
- Verifying API credentials
- Making a simple test call to the LLM
- Displaying response time and results
"""

import sys

from quarto4sbp.llm.client import LLMClient
from quarto4sbp.llm.config import load_config


def cmd_llm(args: list[str]) -> int:
    """Test LLM connectivity and configuration.

    Args:
        args: Command line arguments (expects 'test' subcommand)

    Returns:
        0 on success, 1 on failure
    """
    # Check for subcommand
    if not args or args[0] != "test":
        print("Usage: q4s llm test", file=sys.stderr)
        print("", file=sys.stderr)
        print("Test LLM connectivity and configuration.", file=sys.stderr)
        return 1

    print("Testing LLM connectivity...")
    print("")

    # Load configuration
    try:
        config = load_config()
        print("✓ Configuration loaded successfully")
        print(f"  Model: {config.model}")
        if config.base_url:
            print(f"  Base URL: {config.base_url}")
        print(f"  Max tokens: {config.max_tokens}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Timeout: {config.timeout}s")
        print("")
    except ValueError as e:
        print(f"✗ Configuration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}", file=sys.stderr)
        return 1

    # Create client
    try:
        client = LLMClient(config)
        print("✓ LLM client initialized")
        print("")
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}", file=sys.stderr)
        return 1

    # Test connectivity
    print("Testing API connectivity...")
    result = client.test_connectivity()

    if result["success"]:
        print("✓ API call successful")
        print(f"  Response: {result['response']}")
        print(f"  Elapsed time: {result['elapsed_time']:.2f}s")
        print("")
        print("LLM integration is working correctly!")
        return 0
    else:
        print(f"✗ API call failed: {result['error']}", file=sys.stderr)
        print(f"  Elapsed time: {result['elapsed_time']:.2f}s", file=sys.stderr)
        print("", file=sys.stderr)
        print("Troubleshooting:", file=sys.stderr)
        print("- Verify OPENAI_API_KEY is set correctly", file=sys.stderr)
        print("- Check network connectivity", file=sys.stderr)
        print("- Verify API endpoint URL", file=sys.stderr)
        print("- Check API key permissions", file=sys.stderr)
        return 1
