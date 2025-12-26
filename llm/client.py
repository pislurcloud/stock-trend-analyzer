import os
import logging
from typing import List

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Lightweight LLM client with provider fallback.

    Priority:
    1. OpenAI (if OPENAI_API_KEY is set)
    2. OpenRouter free models (if OPENROUTER_API_KEY is set)
    """

    def __init__(self, models: List[str] | None = None):
        # Default model priority list
        self.models = models or [
            "gpt-4o-mini",
            "meta-llama/llama-3.3-70b-instruct:free",
        ]

        self.clients = []

        # OpenAI client
        if os.getenv("OPENAI_API_KEY"):
            self.clients.append(
                (
                    "openai",
                    OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
                )
            )

        # OpenRouter client
        if os.getenv("OPENROUTER_API_KEY"):
            self.clients.append(
                (
                    "openrouter",
                    OpenAI(
                        api_key=os.getenv("OPENROUTER_API_KEY"),
                        base_url="https://openrouter.ai/api/v1",
                    ),
                )
            )

        if not self.clients:
            raise RuntimeError(
                "No LLM providers available. "
                "Set OPENAI_API_KEY or OPENROUTER_API_KEY."
            )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_error = None

        for provider, client in self.clients:
            for model in self.models:
                try:
                    logger.info(f"[LLM] Trying {provider} model: {model}")

                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.4,
                    )

                    return response.choices[0].message.content.strip()

                except Exception as e:
                    logger.warning(
                        f"[LLM] {provider} model {model} failed: {e}"
                    )
                    last_error = e

        raise RuntimeError(
            f"All LLM models failed. Last error: {last_error}"
        )
