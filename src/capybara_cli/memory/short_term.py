from __future__ import annotations

from collections import deque
from typing import Any


class ShortTermMemory:
    def __init__(self, max_messages: int = 100, context_window: int = 128000):
        self.max_messages = max_messages
        self.context_window = context_window
        self.messages: deque[dict[str, Any]] = deque(maxlen=max_messages)
        self.total_tokens = 0
    
    def add_message(self, role: str, content: str, **kwargs):
        message = {
            "role": role,
            "content": content,
            "tokens": len(content.split()) * 2,
            **kwargs,
        }
        
        self.messages.append(message)
        self.total_tokens += message["tokens"]
        
        self._prune_if_needed()
    
    def get_messages(self, limit: int | None = None) -> list[dict[str, Any]]:
        messages = list(self.messages)
        if limit:
            messages = messages[-limit:]
        return messages
    
    def clear(self):
        self.messages.clear()
        self.total_tokens = 0
    
    def summarize(self) -> str:
        if not self.messages:
            return ""
        
        user_msgs = [m for m in self.messages if m["role"] == "user"]
        assistant_msgs = [m for m in self.messages if m["role"] == "assistant"]
        
        summary = f"Conversation with {len(user_msgs)} user messages and {len(assistant_msgs)} assistant responses."
        
        if user_msgs:
            summary += f" Last user message: {user_msgs[-1]['content'][:100]}..."
        
        return summary
    
    def _prune_if_needed(self):
        while self.total_tokens > self.context_window and len(self.messages) > 1:
            removed = self.messages.popleft()
            self.total_tokens -= removed["tokens"]
