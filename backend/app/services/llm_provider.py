"""
LLM provider abstraction - swap between NVIDIA NIM, Ollama, or OpenAI.

Supported providers (set via LLM_PROVIDER env var):
  nim     - NVIDIA NIM API (OpenAI-compatible, free tier)
  ollama  - local Ollama server (OpenAI-compatible)
  openai  - OpenAI API

All providers expose an OpenAI-compatible endpoint, so both the PydanticAI
model and the raw AsyncOpenAI client use the same openai SDK under the hood.
"""
import logging
import os

import openai
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider configuration defaults
# ---------------------------------------------------------------------------

_PROVIDER_DEFAULTS: dict[str, dict] = {
    "nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "chat_model": "meta/llama-3.1-8b-instruct",
        "embedding_model": "nvidia/nv-embedqa-e5-v5",
        "embedding_dims": 1024,
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,  # Ollama does not require a key
        "chat_model": "llama3.1",
        "embedding_model": "nomic-embed-text",
        "embedding_dims": 768,
    },
    "openai": {
        "base_url": None,  # Use the default OpenAI endpoint
        "api_key_env": "OPENAI_API_KEY",
        "chat_model": "gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
        "embedding_dims": 1536,
    },
}


def _resolve_config() -> dict:
    """Read env vars and return the resolved provider configuration."""
    provider = os.getenv("LLM_PROVIDER", "nim").lower()
    if provider not in _PROVIDER_DEFAULTS:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. "
            f"Valid values: {list(_PROVIDER_DEFAULTS)}"
        )
    defaults = _PROVIDER_DEFAULTS[provider]

    api_key: str | None = None
    if defaults["api_key_env"]:
        api_key = os.getenv(defaults["api_key_env"])
        if not api_key:
            raise EnvironmentError(
                f"LLM_PROVIDER='{provider}' requires {defaults['api_key_env']} "
                "to be set in the environment."
            )
    else:
        api_key = "ollama"  # Ollama accepts any non-empty string

    base_url: str | None = os.getenv("LLM_BASE_URL") or defaults["base_url"]
    chat_model: str = os.getenv("LLM_MODEL") or defaults["chat_model"]
    embedding_model: str = (
        os.getenv("EMBEDDING_MODEL") or defaults["embedding_model"]
    )
    embedding_dims: int = int(
        os.getenv("EMBEDDING_DIMENSIONS") or defaults["embedding_dims"]
    )

    logger.info(
        "LLM provider resolved: provider=%s chat_model=%s embedding_model=%s",
        provider,
        chat_model,
        embedding_model,
    )
    return {
        "provider": provider,
        "base_url": base_url,
        "api_key": api_key,
        "chat_model": chat_model,
        "embedding_model": embedding_model,
        "embedding_dims": embedding_dims,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_chat_model() -> OpenAIModel:
    """Return a PydanticAI OpenAIModel configured for the active provider.

    Use this when constructing a pydantic_ai.Agent.

    Example::

        from app.services.llm_provider import get_chat_model
        from pydantic_ai import Agent

        agent = Agent(model=get_chat_model(), system_prompt="...")
    """
    config = _resolve_config()
    provider = OpenAIProvider(
        base_url=config["base_url"],
        api_key=config["api_key"],
    )
    return OpenAIModel(config["chat_model"], provider=provider)


def get_raw_client() -> openai.AsyncOpenAI:
    """Return a raw AsyncOpenAI client configured for the active provider.

    Use this for embeddings and any direct API call that PydanticAI does not
    handle (e.g. openai.embeddings.create).

    Example::

        from app.services.llm_provider import get_raw_client

        client = get_raw_client()
        response = await client.embeddings.create(...)
    """
    config = _resolve_config()
    kwargs: dict = {"api_key": config["api_key"]}
    if config["base_url"]:
        kwargs["base_url"] = config["base_url"]
    return openai.AsyncOpenAI(**kwargs)


def get_embedding_config() -> dict[str, str | int]:
    """Return embedding model name and vector dimensions for the active provider.

    Returns a dict with keys ``model`` (str) and ``dimensions`` (int).
    """
    config = _resolve_config()
    return {
        "model": config["embedding_model"],
        "dimensions": config["embedding_dims"],
    }
