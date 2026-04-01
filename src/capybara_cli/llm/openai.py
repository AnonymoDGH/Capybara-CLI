from __future__ import annotations

from typing import AsyncIterator

import httpx

from .base import BaseLLMProvider, LLMResponse, Message


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str = "gpt-4-turbo-preview", api_key: str | None = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.api_base = self.api_base or "https://api.openai.com/v1"
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={"Authorization": f"Bearer {self.api_key}"},
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
        
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]
            payload["tool_choice"] = kwargs.get("tool_choice", "auto")
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        choice = data["choices"][0]
        message = choice["message"]
        
        return LLMResponse(
            content=message.get("content", ""),
            input_tokens=data["usage"]["prompt_tokens"],
            output_tokens=data["usage"]["completion_tokens"],
            model=data["model"],
            finish_reason=choice["finish_reason"],
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
        try:
            import tiktoken
            encoder = tiktoken.encoding_for_model(self.model)
            return len(encoder.encode(text))
        except:
            return len(text.split())
