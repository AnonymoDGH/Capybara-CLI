from __future__ import annotations

from typing import AsyncIterator

import httpx

from .base import BaseLLMProvider, LLMResponse, Message, Role


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str | None = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.api_base = self.api_base or "https://api.anthropic.com/v1"
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=self.timeout,
        )
    
    async def chat(self, messages: list[Message], **kwargs) -> LLMResponse:
        system_msg = ""
        chat_messages = []
        
        for m in messages:
            if m.role == Role.SYSTEM:
                system_msg = m.content
            else:
                chat_messages.append({
                    "role": "user" if m.role == Role.USER else "assistant",
                    "content": m.content,
                })
        
        payload = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
        
        response = await self.client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()
        
        content = ""
        tool_calls = []
        
        for block in data["content"]:
            if block["type"] == "text":
                content += block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append({
                    "id": block["id"],
                    "type": "function",
                    "function": {
                        "name": block["name"],
                        "arguments": block["input"],
                    }
                })
        
        return LLMResponse(
            content=content,
            input_tokens=data["usage"]["input_tokens"],
            output_tokens=data["usage"]["output_tokens"],
            model=data["model"],
            finish_reason=data["stop_reason"],
            tool_calls=tool_calls,
        )
    
    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]:
        system_msg = ""
        chat_messages = []
        
        for m in messages:
            if m.role == Role.SYSTEM:
                system_msg = m.content
            else:
                chat_messages.append({
                    "role": "user" if m.role == Role.USER else "assistant",
                    "content": m.content,
                })
        
        payload = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": True,
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        async with self.client.stream("POST", "/messages", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json
                    event = json.loads(data)
                    if event["type"] == "content_block_delta":
                        if event["delta"]["type"] == "text_delta":
                            yield event["delta"]["text"]
    
    def count_tokens(self, text: str) -> int:
        return len(text.split()) * 2
