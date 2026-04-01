from __future__ import annotations

from typing import AsyncIterator

import httpx

from .base import BaseLLMProvider, LLMResponse, Message


class NVIDIAProvider(BaseLLMProvider):
    DEFAULT_MODELS = {
        "llama-3.1-405b": "meta/llama-3.1-405b-instruct",
        "llama-3.1-70b": "meta/llama-3.1-70b-instruct",
        "llama-3.1-8b": "meta/llama-3.1-8b-instruct",
        "nemotron-4-340b": "nvidia/nemotron-4-340b-instruct",
        "mixtral-8x22b": "mistralai/mixtral-8x22b-instruct-v0.1",
        "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct-v0.1",
        "arctic": "snowflake/arctic",
        "dbrx": "databricks/dbrx-instruct",
        "fuyu-8b": "adept/fuyu-8b",
        "kosmos-2": "microsoft/kosmos-2",
        "phi-3": "microsoft/phi-3-medium-4k-instruct",
        "starcoder2": "bigcode/starcoder2-15b",
        "gemma-2-27b": "google/gemma-2-27b-it",
        "gemma-2-9b": "google/gemma-2-9b-it",
    }
    
    def __init__(self, model: str = "llama-3.1-405b", api_key: str | None = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.api_base = self.api_base or "https://integrate.api.nvidia.com/v1"
        self._resolve_model()
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        )
    
    def _resolve_model(self):
        if self.model in self.DEFAULT_MODELS:
            self.model = self.DEFAULT_MODELS[self.model]
    
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
        return len(text.split()) * 2
