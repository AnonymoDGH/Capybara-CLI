"""Memory manager for Capybara CLI."""

from __future__ import annotations

from typing import Any

try:
    from ..config import MemoryConfig
    from .long_term import LongTermMemory
    from .short_term import ShortTermMemory
except ImportError:
    from config import MemoryConfig
    from long_term import LongTermMemory
    from short_term import ShortTermMemory


class MemoryManager:
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.short_term = ShortTermMemory(
            max_messages=config.max_history_messages,
            context_window=config.context_window,
        )
        self.long_term = LongTermMemory(
            persistence_path=config.persistence_path,
        ) if config.type in ("long_term", "hybrid") else None
    
    def add_message(self, role: str, content: str, **kwargs):
        self.short_term.add_message(role, content, **kwargs)
        
        if self.long_term and kwargs.get("important"):
            self.long_term.store_interaction(content, kwargs.get("metadata", {}))
    
    def get_messages(self, limit: int | None = None) -> list[dict[str, Any]]:
        return self.short_term.get_messages(limit)
    
    def get_context(self) -> str:
        messages = self.short_term.get_messages()
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    def clear(self):
        self.short_term.clear()
        if self.long_term:
            self.long_term.clear()
    
    def summarize(self) -> str:
        return self.short_term.summarize()
    
    def search(self, query: str) -> list[dict[str, Any]]:
        if self.long_term:
            return self.long_term.search(query)
        return []
