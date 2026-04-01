from __future__ import annotations

from typing import AsyncIterator

import httpx

from .base import BaseLLMProvider, LLMResponse, Message


class LocalProvider(BaseLLMProvider):
    def __init__(self, model: str = "local-model", api_key: str | None = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.api_base = self.api_base or "http://localhost:11434/v1"
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            timeout=self.timeout,
        )
    
    async def chat(self, messages: list[Message], **kwargs) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": self._prepare_messages(messages),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", self.top_p),
        }
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        choice = data["choices"][0]
        message = choice["message"]
        
        return LLMResponse(
            content=message.get("content", ""),
            input_tokens=data.get("usage", {}).get("prompt_tokens", 0),
            output_tokens=data.get("usage", {}).get("completion_tokens", 0),
            model=data.get("model", self.model),
            finish_reason=choice.get("finish_reason", ""),
            tool_calls=message.get("tool_calls", []),
        )
    
    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": self._prepare_messages(messages),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": True,
        }
        
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json
                    chunk = json.loads(data)
                    if chunk["choices"][0].get("delta", {}).get("content"):
                        yield chunk["choices"][0]["delta"]["content"]
    
    def count_tokens(self, text: str) -> int:
        return len(text.split()) * 2
