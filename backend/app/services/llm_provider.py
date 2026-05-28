"""
LLM provider abstraction — swap between OpenAI, NVIDIA NIM, or local Ollama.
"""
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    async def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError
