from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Callable


class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    role: Role
    content: str
    name: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None


@dataclass
class LLMResponse:
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    finish_reason: str = ""
    tool_calls: list[dict] = field(default_factory=list)


class BaseLLMProvider(ABC):
    def __init__(self, model: str, api_key: str | None = None, api_base: str | None = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 4096)
        self.top_p = kwargs.get("top_p", 0.95)
        self.timeout = kwargs.get("timeout", 120)
        self.max_retries = kwargs.get("max_retries", 3)
    
    @abstractmethod
    async def chat(self, messages: list[Message], **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]:
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
    
    def _prepare_messages(self, messages: list[Message]) -> list[dict]:
        return [
            {
                "role": m.role.value,
                "content": m.content,
                **({"name": m.name} if m.name else {}),
                **({"tool_calls": m.tool_calls} if m.tool_calls else {}),
                **({"tool_call_id": m.tool_call_id} if m.tool_call_id else {}),
            }
            for m in messages
        ]
