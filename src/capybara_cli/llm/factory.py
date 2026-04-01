"""Factory for creating LLM providers."""

from __future__ import annotations

try:
    from .anthropic import AnthropicProvider
    from .base import BaseLLMProvider
    from .google import GoogleProvider
    from .local import LocalProvider
    from .nvidia import NVIDIAProvider
    from .openai import OpenAIProvider
except ImportError:
    from anthropic import AnthropicProvider
    from base import BaseLLMProvider
    from google import GoogleProvider
    from local import LocalProvider
    from nvidia import NVIDIAProvider
    from openai import OpenAIProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "nvidia": NVIDIAProvider,
    "google": GoogleProvider,
    "local": LocalProvider,
    "ollama": LocalProvider,
    "lmstudio": LocalProvider,
    "textgen": LocalProvider,
}


def create_provider(provider: str, model: str | None = None, **kwargs) -> BaseLLMProvider:
    provider = provider.lower()
    
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
    
    provider_class = PROVIDERS[provider]
    
    if model is None:
        model = _get_default_model(provider)
    
    return provider_class(model=model, **kwargs)


def _get_default_model(provider: str) -> str:
    defaults = {
        "openai": "gpt-4-turbo-preview",
        "anthropic": "claude-3-5-sonnet-20241022",
        "nvidia": "llama-3.1-405b",
        "google": "gemini-1.5-pro",
        "local": "local-model",
        "ollama": "llama3.1",
        "lmstudio": "local-model",
        "textgen": "local-model",
    }
    return defaults.get(provider, "default-model")


def list_available_providers() -> list[str]:
    return list(PROVIDERS.keys())


def list_models_for_provider(provider: str) -> list[str]:
    models = {
        "openai": ["gpt-4-turbo-preview", "gpt-4", "gpt-4o", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"],
        "nvidia": ["llama-3.1-405b", "llama-3.1-70b", "llama-3.1-8b", "nemotron-4-340b", "mixtral-8x22b", "mixtral-8x7b"],
        "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
        "local": ["local-model"],
        "ollama": ["llama3.1", "llama3", "mistral", "codellama", "qwen2.5-coder"],
    }
    return models.get(provider, [])
