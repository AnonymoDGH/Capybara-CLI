import pytest
from pathlib import Path
from capybara_cli.config import Config, LLMConfig, AgentConfig, load_config


def test_default_config():
    config = Config()
    assert config.llm.provider == "openai"
    assert config.llm.model == "gpt-4-turbo-preview"
    assert config.agent.max_iterations == 10


def test_config_from_dict():
    data = {
        "llm": {"provider": "nvidia", "model": "llama-3.1-405b"},
        "agent": {"max_iterations": 20},
    }
    config = Config.from_dict(data)
    assert config.llm.provider == "nvidia"
    assert config.llm.model == "llama-3.1-405b"
    assert config.agent.max_iterations == 20


def test_config_to_dict():
    config = Config()
    data = config.to_dict()
    assert "llm" in data
    assert "agent" in data
    assert data["llm"]["provider"] == "openai"
