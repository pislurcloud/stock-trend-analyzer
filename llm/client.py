import os
import logging
from openai import OpenAI, APIStatusError

logging.basicConfig(level=logging.INFO)


class LLMClient:
    """
    Provider-aware LLM client with strict routing.

    Rules:
    - OpenAI models → OpenAI API
    - Everything else → OpenRouter
    """

    def __init__(self, models: list[str]):
        if not models:
            raise ValueError("At least one model must be provided")

        self.models = models

        self.openai_client = None
        self.openrouter_client = None

        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

        if os.getenv("OPENROUTER_API_KEY"):
            self.openrouter_client = OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=os.getenv(
                    "OPENROUTER_BASE_URL",
                    "https://openrouter.ai/api/v1"
                )
            )

        if not self.openai_client and not self.openrouter_client:
            raise RuntimeError(
                "No LLM clients available. Set OPENAI_API_KEY or OPENROUTER_API_KEY."
            )

    def _select_client(self, model: str):
        """
        Decide which client to use based on model name.
        """
        # Explicit OpenAI models
        if model in {"gpt-4o-mini", "gpt-4.1", "gpt-4o"}:
            if not self.openai_client:
                raise RuntimeError("OpenAI API key not configured")
            return self.openai_client, model, "OpenAI"

        # Everything else goes to OpenRouter
        if not self.openrouter_client:
            raise RuntimeError("OpenRouter API key not configured")
        return self.openrouter_client, model, "OpenRouter"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_error = None

        for model in self.models:
            try:
                client, model_name, provider = self._select_client(model)

                logging.info(f"[LLM] Trying {provider} model: {model_name}")

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                )

                return response.choices[0].message.content.strip()

            except APIStatusError as e:
                logging.warning(
                    f"[LLM] {provider} model {model} failed "
                    f"with {e.status_code}"
                )
                last_error = e
                continue

            except Exception as e:
                logging.warning(
                    f"[LLM] Model {model} failed: {e}"
                )
                last_error = e
                continue

        raise RuntimeError(
            f"All LLM models failed. Last error: {last_error}"
        )
