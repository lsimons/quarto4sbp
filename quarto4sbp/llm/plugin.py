from typing import Any, Callable

from llm.default_plugins.openai_models import AsyncChat, Chat

import llm


@llm.hookimpl
def register_models(register: Callable[..., Any]) -> None:
    for model in [
        "azure/gpt-5-mini",
        "azure/gpt-5",
    ]:
        register(
            Chat(
                model,
                vision=True,
                reasoning=True,
                supports_schema=True,
                supports_tools=True,
            ),
            AsyncChat(
                model,
                vision=True,
                reasoning=True,
                supports_schema=True,
                supports_tools=True,
            ),
        )

    register(
        Chat("aws/claude-4-5-sonnet"),
        AsyncChat("aws/claude-4-5-sonnet"),
    )
