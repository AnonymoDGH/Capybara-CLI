import pytest
from capybara_cli.llm import create_provider, list_available_providers
from capybara_cli.llm.nvidia import NVIDIAProvider


def test_list_providers():
    providers = list_available_providers()
    assert "openai" in providers
    assert "nvidia" in providers
    assert "anthropic" in providers
    assert "google" in providers


def test_nvidia_provider_models():
    provider = NVIDIAProvider(api_key="test")
    assert "llama-3.1-405b" in provider.DEFAULT_MODELS
    assert "nemotron-4-340b" in provider.DEFAULT_MODELS


def test_nvidia_model_resolution():
    provider = NVIDIAProvider(model="llama-3.1-405b", api_key="test")
    assert "meta/llama-3.1-405b-instruct" in provider.model
