"""Configuration management for Capybara CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "nvidia"
    model: str = "llama-3.1-405b"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.95
    timeout: int = 120
    max_retries: int = 3
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = self._get_api_key_from_env()
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "cohere": "COHERE_API_KEY",
            "nvidia": "NVIDIA_API_KEY",
        }
        env_var = env_vars.get(self.provider, f"{self.provider.upper()}_API_KEY")
        return os.getenv(env_var)


@dataclass
class AgentConfig:
    """Agent behavior configuration."""
    max_iterations: int = 10
    timeout_seconds: int = 300
    auto_confirm: bool = False
    verbose: bool = True
    max_tool_calls: int = 50
    planning_enabled: bool = True
    reflection_enabled: bool = True
    learning_enabled: bool = True


@dataclass
class ToolConfig:
    """Tool system configuration."""
    enabled: list[str] = field(default_factory=lambda: [
        "bash", "file_read", "file_edit", "search", "git", 
        "code_execution", "web_search", "code_analysis"
    ])
    disabled: list[str] = field(default_factory=list)
    require_confirmation: list[str] = field(default_factory=lambda: [
        "file_delete", "bash_rm", "git_push"
    ])
    timeout_seconds: int = 60
    max_output_length: int = 10000


@dataclass
class MemoryConfig:
    """Memory system configuration."""
    type: str = "hybrid"
    context_window: int = 128000
    cache_enabled: bool = True
    summarization_threshold: int = 8000
    max_history_messages: int = 100
    persistence_path: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security and safety configuration."""
    sandbox_enabled: bool = True
    allowed_commands: list[str] = field(default_factory=lambda: [
        "ls", "cat", "grep", "find", "head", "tail", "wc", "echo"
    ])
    blocked_patterns: list[str] = field(default_factory=lambda: [
        r"rm\s+-rf\s+/",
        r">\s*/dev/",
        r":\(\)\{\s*:\|\:&\s*\};:",
        r"curl.*\|.*sh",
        r"wget.*\|.*sh",
        r"mkfs",
        r"dd\s+if=",
        r"\bsu\b",
        r"\bsudo\b",
    ])
    scan_for_secrets: bool = True
    auto_fix_security_issues: bool = False


@dataclass
class Config:
    """Main configuration class."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Create Config from dictionary."""
        return cls(
            llm=LLMConfig(**data.get("llm", {})),
            agent=AgentConfig(**data.get("agent", {})),
            tools=ToolConfig(**data.get("tools", {})),
            memory=MemoryConfig(**data.get("memory", {})),
            security=SecurityConfig(**data.get("security", {})),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert Config to dictionary."""
        return {
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "api_key": "***" if self.llm.api_key else None,
                "api_base": self.llm.api_base,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "top_p": self.llm.top_p,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries,
            },
            "agent": {
                "max_iterations": self.agent.max_iterations,
                "timeout_seconds": self.agent.timeout_seconds,
                "auto_confirm": self.agent.auto_confirm,
                "verbose": self.agent.verbose,
                "max_tool_calls": self.agent.max_tool_calls,
                "planning_enabled": self.agent.planning_enabled,
                "reflection_enabled": self.agent.reflection_enabled,
                "learning_enabled": self.agent.learning_enabled,
            },
            "tools": {
                "enabled": self.tools.enabled,
                "disabled": self.tools.disabled,
                "require_confirmation": self.tools.require_confirmation,
                "timeout_seconds": self.tools.timeout_seconds,
                "max_output_length": self.tools.max_output_length,
            },
            "memory": {
                "type": self.memory.type,
                "context_window": self.memory.context_window,
                "cache_enabled": self.memory.cache_enabled,
                "summarization_threshold": self.memory.summarization_threshold,
                "max_history_messages": self.memory.max_history_messages,
                "persistence_path": self.memory.persistence_path,
            },
            "security": {
                "sandbox_enabled": self.security.sandbox_enabled,
                "allowed_commands": self.security.allowed_commands,
                "blocked_patterns": self.security.blocked_patterns,
                "scan_for_secrets": self.security.scan_for_secrets,
                "auto_fix_security_issues": self.security.auto_fix_security_issues,
            },
        }


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    if os.name == "nt":
        config_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    
    capybara_dir = config_dir / "capybara"
    capybara_dir.mkdir(parents=True, exist_ok=True)
    return capybara_dir / "config.yaml"


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file or create default."""
    if config_path is None:
        config_path = get_default_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return Config.from_dict(data)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration.")
    
    return Config()


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """Save configuration to file."""
    if config_path is None:
        config_path = get_default_config_path()
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)


def create_default_config_file(config_path: Optional[Path] = None) -> Path:
    """Create a default configuration file."""
    if config_path is None:
        config_path = get_default_config_path()
    
    default_config = Config()
    save_config(default_config, config_path)
    return config_path
