"""Azure AI API model handler implementation, with Ollama support."""

import os
from typing import Any

import aiohttp
from readmeai.config.settings import ConfigLoader
from readmeai.extractors.models import RepositoryContext
from readmeai.models.base import BaseModelHandler
from readmeai.models.enums import BaseURLs, LLMProviders
from readmeai.models.tokens import token_handler
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class AzureAIHandler(BaseModelHandler):
    """
    Azure AI model handler implementation.
    """

    def __init__(self, config_loader: ConfigLoader, context: RepositoryContext) -> None:
        super().__init__(config_loader, context)
        self._model_settings()

    def _model_settings(self):
        """Handles Azure AI."""
        self.base_url = self.config.llm.base_url
        self.model = self.config.llm.model
        self.max_tokens = self.config.llm.tokens
        self.model = self.config.llm.model
        self.resource = self.config.llm.resource
        self.top_p = self.config.llm.top_p


        self.url=f"{self.base_url}{self.resource}"


        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key is None:
            raise ValueError("OpenAI API key not set in environment.")
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def _build_payload(self, prompt: str) -> dict[str, Any]:
        """Build request body for making text generation requests."""
        return {
            "messages": [
                {
                    "role": "system",
                    "content": self.system_message,
                },
                {"role": "user", "content": prompt},
            ],
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(
            (
                aiohttp.ClientError,
                aiohttp.ClientResponseError,
                aiohttp.ClientConnectorError,
            ),
        ),
    )
    async def _make_request(
        self,
        index: str | None,
        prompt: str | None,
        tokens: int | None,
        repo_files: Any,
    ):
        """Process requests to OpenAI API, with retries and error handling."""
        try:
            if prompt is None:
                raise ValueError("Prompt cannot be None")

            prompt = await token_handler(
                config=self.config,
                index=index,
                prompt=prompt,
                tokens=tokens,
            )
            if not prompt:
                raise ValueError("Token handler returned empty prompt")

            if index == "file_summary":
                self.max_tokens = 100

            parameters = await self._build_payload(prompt)

            async with self._session.post(
                self.url,
                headers=self.headers,
                json=parameters,
            ) as response:
                response.raise_for_status()
                response = await response.json()
                content = response["choices"][0]["message"]["content"]

                if not content:
                    raise ValueError("Empty response from API")

                self._logger.info(
                    f"Response from {self.config.llm.api.capitalize()} for '{index}': {content}",
                )
                return index, content

        except (
            aiohttp.ClientError,
            aiohttp.ClientResponseError,
            aiohttp.ClientConnectorError,
        ) as e:
            self._logger.error(f"Error processing request for '{index}': {e!r}")
            raise  # Re-raise for retry decorator

        except Exception as e:
            self._logger.error(f"Unexpected error for '{index}': {e!r}")
            return index, self.placeholder
